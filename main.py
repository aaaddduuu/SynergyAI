import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Set
import uuid
from datetime import datetime
from functools import wraps

from core.storage import Session, Storage, Task, TaskState, AgentRole, Message
from core.model_config import model_config_manager, ModelConfig, AgentModelConfig, MODEL_OPTIONS, PROVIDER_BASE_URLS
from core.orchestrator import MultiAgentOrchestrator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(logs_dir, "app.log"),
            maxBytes=10*1024*1024,
            backupCount=5
        ),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ai_coworker")

app = FastAPI(
    title="SynergyAI",
    description="Multi-Agent Collaboration Platform - Where AI Agents Work Synergistically",
    version="1.0.0"
)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

storage = Storage()
orchestrator: Optional[MultiAgentOrchestrator] = None
current_session: Optional[Session] = None


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    logger.warning(f"API Error: {exc.message} - {exc.details}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "message": str(exc) if os.getenv("DEBUG") else "请联系管理员",
            "timestamp": datetime.now().isoformat()
        }
    )


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_count = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_count += 1
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast message: {e}")


manager = ConnectionManager()


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("消息不能为空")
        if len(v) > 10000:
            raise ValueError("消息长度不能超过10000字符")
        return v.strip()


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    assignee: Optional[str] = None
    assignee_role: Optional[str] = None
    priority: str = "medium"
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("任务标题不能为空")
        if len(v) > 200:
            raise ValueError("任务标题不能超过200字符")
        return v.strip()
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError("优先级必须是 low, medium 或 high")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    assignee_role: Optional[str] = None
    state: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[List[str]] = None
    
    @validator('state')
    def validate_state(cls, v):
        if v and v not in ['pending', 'in_progress', 'review', 'done', 'blocked']:
            raise ValueError("无效的任务状态")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high']:
            raise ValueError("优先级必须是 low, medium 或 high")
        return v


class ConfigRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed = ['openai', 'anthropic', 'zhipu', 'custom']
        if v not in allowed:
            raise ValueError(f"Provider must be one of: {allowed}")
        return v


class AgentConfigRequest(BaseModel):
    role: str
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    
    @validator('role')
    def validate_role(cls, v):
        allowed = ['hr', 'pm', 'ba', 'dev', 'qa', 'architect']
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed = ['openai', 'anthropic', 'zhipu', 'custom']
        if v not in allowed:
            raise ValueError(f"Provider must be one of: {allowed}")
        return v


class BatchConfigRequest(BaseModel):
    configs: List[AgentConfigRequest]


def log_request(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Request: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Success: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper


@app.get("/", response_class=HTMLResponse)
@log_request
async def index(request: Request):
    logger.info("Index page accessed")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/config")
@log_request
async def configure(req: ConfigRequest):
    try:
        base_url = req.base_url or PROVIDER_BASE_URLS.get(req.provider, "")
        
        config = ModelConfig(
            provider=req.provider,
            model=req.model,
            api_key=req.api_key or "",
            base_url=base_url,
            temperature=req.temperature
        )
        
        model_config_manager.set_default_config(config)
        
        await manager.broadcast({
            "type": "config_updated",
            "provider": req.provider,
            "model": req.model
        })
        logger.info(f"LLM configured: {req.provider}/{req.model}")
        return {"status": "ok", "message": f"默认模型配置成功: {req.provider}/{req.model}"}
    except Exception as e:
        logger.error(f"Config error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/config/agent")
async def configure_agent(req: AgentConfigRequest):
    try:
        base_url = req.base_url or PROVIDER_BASE_URLS.get(req.provider, "")
        
        config = AgentModelConfig(
            role=req.role,
            provider=req.provider,
            model=req.model,
            api_key=req.api_key or "",
            base_url=base_url,
            temperature=req.temperature
        )
        
        model_config_manager.set_agent_config(req.role, config)
        
        logger.info(f"Agent {req.role} configured: {req.provider}/{req.model}")
        return {"status": "ok", "message": f"{req.role} 角色配置成功: {req.provider}/{req.model}"}
    except Exception as e:
        logger.error(f"Agent config error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/config/agents")
async def configure_agents(req: BatchConfigRequest):
    try:
        for config_req in req.configs:
            base_url = config_req.base_url or PROVIDER_BASE_URLS.get(config_req.provider, "")
            
            config = AgentModelConfig(
                role=config_req.role,
                provider=config_req.provider,
                model=config_req.model,
                api_key=config_req.api_key or "",
                base_url=base_url,
                temperature=config_req.temperature
            )
            
            model_config_manager.set_agent_config(config_req.role, config)
        
        logger.info(f"Batch configured {len(req.configs)} agents")
        return {"status": "ok", "message": f"批量配置成功: {len(req.configs)} 个角色"}
    except Exception as e:
        logger.error(f"Batch config error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/config")
async def get_config():
    try:
        default_config = model_config_manager.get_default_config()

        # 构建默认配置响应（确保所有字段都有值）
        default_response = {
            "provider": default_config.provider or "openai",
            "model": default_config.model or "gpt-4o",
            "base_url": default_config.base_url or "",
            "temperature": default_config.temperature or 0.7,
            "has_api_key": bool(default_config.api_key)
        }

        # 构建各个 Agent 的配置
        agent_configs = {}
        for role in ['hr', 'pm', 'ba', 'dev', 'qa', 'architect']:
            config = model_config_manager.get_agent_config(role)
            if config:
                agent_configs[role] = {
                    "provider": config.provider or "openai",
                    "model": config.model or "gpt-4o",
                    "base_url": config.base_url or "",
                    "temperature": config.temperature or 0.7,
                    "has_api_key": bool(config.api_key)
                }
            else:
                # 如果该角色没有配置，使用默认配置
                agent_configs[role] = {
                    "provider": default_config.provider or "openai",
                    "model": default_config.model or "gpt-4o",
                    "base_url": default_config.base_url or "",
                    "temperature": default_config.temperature or 0.7,
                    "has_api_key": bool(default_config.api_key)
                }

        return {
            "default": default_response,
            "agents": agent_configs,
            "providers": list(MODEL_OPTIONS.keys()),
            "models": MODEL_OPTIONS
        }
    except Exception as e:
        logger.error(f"Get config error: {str(e)}", exc_info=True)
        # 返回安全的默认配置
        return {
            "default": {
                "provider": "openai",
                "model": "gpt-4o",
                "base_url": "",
                "temperature": 0.7,
                "has_api_key": False
            },
            "agents": {},
            "providers": list(MODEL_OPTIONS.keys()),
            "models": MODEL_OPTIONS
        }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket连接成功"
        })
        logger.info("WebSocket connection established")

        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(data, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "message": str(e)
        }, websocket)


async def handle_websocket_message(data: dict, websocket: WebSocket):
    global current_session, orchestrator

    msg_type = data.get("type")
    logger.info(f"WS Message type: {msg_type}")
    
    if msg_type == "chat":
        message = data.get("message", "")
        
        if not current_session:
            await manager.send_personal_message({
                "type": "error",
                "message": "请先创建项目"
            }, websocket)
            return

        if not current_session.is_active:
            await manager.send_personal_message({
                "type": "error",
                "message": "当前session已结束，请创建新项目"
            }, websocket)
            return

        if not orchestrator:
            await manager.send_personal_message({
                "type": "error",
                "message": "请先配置LLM"
            }, websocket)
            return

        await manager.send_personal_message({
            "type": "message",
            "sender": "user",
            "sender_role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }, websocket)

        try:
            response = orchestrator.chat(current_session, message)
            storage.save_session(current_session)
            logger.info(f"Chat processed, turn: {current_session.turn_count}")

            await manager.send_personal_message({
                "type": "message",
                "sender": response.sender,
                "sender_role": response.sender_role,
                "content": response.content,
                "message_type": response.message_type.value,
                "timestamp": response.timestamp.isoformat()
            }, websocket)

            await manager.send_personal_message({
                "type": "turn_update",
                "turn_count": current_session.turn_count
            }, websocket)

            should_end, reason = current_session.check_session_end()
            if should_end:
                await manager.send_personal_message({
                    "type": "session_end",
                    "reason": reason,
                    "handover_doc": current_session.handover_doc
                }, websocket)

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            await manager.send_personal_message({
                "type": "error",
                "message": f"处理消息失败: {str(e)}"
            }, websocket)

    elif msg_type == "create_session":
        session = Session()
        current_session = session
        storage.save_session(session)
        logger.info(f"Session created: {session.id}")

        await manager.send_personal_message({
            "type": "session_created",
            "session_id": session.id,
            "message": "新项目创建成功！"
        }, websocket)

    elif msg_type == "typing":
        await manager.send_personal_message({
            "type": "typing",
            "sender": data.get("sender", "unknown")
        }, websocket)

    elif msg_type == "ping":
        await manager.send_personal_message({
            "type": "pong"
        }, websocket)


@app.post("/api/session")
@log_request
async def create_session():
    global current_session
    
    session = Session()
    current_session = session
    storage.save_session(session)
    logger.info(f"Session created via API: {session.id}")
    
    await manager.broadcast({
        "type": "session_created",
        "session_id": session.id,
        "message": "新项目创建成功！"
    })
    
    return {"session_id": session.id, "message": "新项目创建成功！"}


@app.get("/api/session")
@log_request
async def get_session():
    if not current_session:
        return {"active": False}
    
    return {
        "active": current_session.is_active,
        "session_id": current_session.id,
        "turn_count": current_session.turn_count,
        "created_at": current_session.created_at.isoformat()
    }


@app.get("/api/sessions")
@log_request
async def list_sessions():
    sessions = storage.list_sessions()
    return {"sessions": sessions}


@app.post("/api/sessions/{session_id}/load")
@log_request
async def load_session(session_id: str):
    global current_session
    session = storage.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    current_session = session
    logger.info(f"Session loaded: {session_id}")
    return {
        "session_id": session.id,
        "turn_count": session.turn_count,
        "message_count": len(session.messages),
        "task_count": len(session.tasks)
    }


@app.get("/api/messages")
@log_request
async def get_messages():
    if not current_session:
        return {"messages": []}
    
    return {
        "messages": [msg.to_dict() for msg in current_session.messages],
        "turn_count": current_session.turn_count
    }


@app.post("/api/chat")
@log_request
async def chat(req: ChatRequest):
    global current_session, orchestrator
    
    if not current_session:
        raise HTTPException(status_code=400, detail="请先创建项目")
    
    if not current_session.is_active:
        raise HTTPException(status_code=400, detail="当前session已结束，请创建新项目")
    
    if not orchestrator:
        raise HTTPException(status_code=400, detail="请先配置LLM")
    
    try:
        response = orchestrator.chat(current_session, req.message)
        storage.save_session(current_session)
        
        return {
            "response": response.to_dict(),
            "turn_count": current_session.turn_count,
            "is_active": current_session.is_active,
            "handover_doc": current_session.handover_doc
        }
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")
@log_request
async def get_tasks():
    if not current_session:
        return {"tasks": []}
    
    return {
        "tasks": [task.to_dict() for task in current_session.tasks.values()]
    }


@app.post("/api/tasks")
@log_request
async def create_task(task: TaskCreate):
    global current_session
    
    if not current_session:
        raise HTTPException(status_code=400, detail="请先创建项目")
    
    new_task = Task(
        id=str(uuid.uuid4()),
        title=task.title,
        description=task.description,
        assignee=task.assignee,
        assignee_role=AgentRole(task.assignee_role) if task.assignee_role else None,
        created_by="user",
        priority=task.priority
    )
    
    current_session.tasks[new_task.id] = new_task
    storage.save_session(current_session)
    logger.info(f"Task created: {new_task.title}")
    
    await manager.broadcast({
        "type": "task_created",
        "task": new_task.to_dict()
    })
    
    return {"task": new_task.to_dict()}


@app.put("/api/tasks/{task_id}")
@log_request
async def update_task(task_id: str, task_update: TaskUpdate):
    global current_session
    
    if not current_session:
        raise HTTPException(status_code=400, detail="请先创建项目")
    
    if task_id not in current_session.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = current_session.tasks[task_id]
    old_state = task.state.value
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.assignee is not None:
        task.assignee = task_update.assignee
    if task_update.assignee_role is not None:
        task.assignee_role = AgentRole(task_update.assignee_role)
    if task_update.state is not None:
        task.state = TaskState(task_update.state)
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.notes is not None:
        task.notes = task_update.notes
    
    task.updated_at = datetime.now()
    
    storage.save_session(current_session)
    logger.info(f"Task updated: {task.title} ({old_state} -> {task.state.value})")
    
    await manager.broadcast({
        "type": "task_updated",
        "task": task.to_dict(),
        "old_state": old_state,
        "new_state": task.state.value
    })
    
    return {"task": task.to_dict()}


@app.delete("/api/tasks/{task_id}")
@log_request
async def delete_task(task_id: str):
    global current_session
    
    if not current_session:
        raise HTTPException(status_code=400, detail="请先创建项目")
    
    if task_id not in current_session.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task_title = current_session.tasks[task_id].title
    del current_session.tasks[task_id]
    storage.save_session(current_session)
    logger.info(f"Task deleted: {task_title}")
    
    await manager.broadcast({
        "type": "task_deleted",
        "task_id": task_id
    })
    
    return {"status": "ok"}


@app.get("/api/agents")
@log_request
async def get_agents():
    from core.agents import AGENT_SYSTEM_PROMPTS, AgentRole
    
    agents = []
    for role in AgentRole:
        if role != AgentRole.ORCHESTRATOR:
            agents.append({
                "role": role.value,
                "name": role.value.upper(),
                "description": AGENT_SYSTEM_PROMPTS[role].split("\n")[0][:50]
            })
    
    return {"agents": agents}


@app.get("/api/handover")
@log_request
async def get_handover():
    if not current_session or not current_session.handover_doc:
        return {"handover": None}
    
    return {"handover": current_session.handover_doc}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "connections": len(manager.active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
