import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Set
import uuid
from datetime import datetime
from functools import wraps
import time
from collections import defaultdict
import asyncio

from core.storage import Session, Storage, Task, TaskState, AgentRole, Message
from core.model_config import model_config_manager, ModelConfig, AgentModelConfig, MODEL_OPTIONS, PROVIDER_BASE_URLS
from core.orchestrator import MultiAgentOrchestrator
from core.auth import auth_manager, User, UserRole, hash_password

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


# ============ 性能监控 ============

class PerformanceMonitor:
    """性能监控工具"""

    def __init__(self):
        self.request_count = 0
        self.response_times = defaultdict(list)
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.slow_queries = []
        self.slow_threshold = 1.0  # 慢请求阈值（秒）

    def record_request(self, path: str, duration: float, status_code: int):
        """记录请求性能"""
        self.request_count += 1
        self.request_counts[path] += 1
        self.response_times[path].append(duration)

        if status_code >= 400:
            self.error_counts[path] += 1

        # 记录慢请求
        if duration > self.slow_threshold:
            self.slow_queries.append({
                "path": path,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            # 只保留最近100条慢请求
            if len(self.slow_queries) > 100:
                self.slow_queries.pop(0)

    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        stats = {
            "total_requests": self.request_count,
            "endpoint_stats": {}
        }

        for path, times in self.response_times.items():
            if times:
                stats["endpoint_stats"][path] = {
                    "count": self.request_counts[path],
                    "errors": self.error_counts[path],
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "p95_time": sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times)
                }

        stats["slow_queries"] = self.slow_queries[-10:]  # 最近10条慢请求

        return stats


perf_monitor = PerformanceMonitor()


# ============ 缓存管理器 ============

class CacheManager:
    """简单的内存缓存管理器"""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key: (value, expiry_time)
        self._lock = asyncio.Lock()

    def _is_expired(self, expiry_time: Optional[float]) -> bool:
        """检查缓存是否过期"""
        if expiry_time is None:
            return False
        return time.time() > expiry_time

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            if key in self._cache:
                value, expiry_time = self._cache[key]
                if not self._is_expired(expiry_time):
                    return value
                # 过期则删除
                del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存（默认5分钟过期）"""
        async with self._lock:
            expiry_time = time.time() + ttl if ttl > 0 else None
            self._cache[key] = (value, expiry_time)

    async def delete(self, key: str):
        """删除缓存"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self):
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self):
        """清理过期缓存"""
        async with self._lock:
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if expiry and self._is_expired(expiry)
            ]
            for key in expired_keys:
                del self._cache[key]


cache_manager = CacheManager()


# ============ 认证相关的 Pydantic 模型 ============

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: str
    password: str
    role: str = "user"

    @validator('username')
    def validate_username(cls, v):
        if not (3 <= len(v) <= 50):
            raise ValueError('用户名长度必须在3-50个字符之间')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('邮箱格式不正确')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少为6个字符')
        return v

    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['admin', 'user', 'guest']
        if v not in valid_roles:
            raise ValueError(f'角色必须是以下之一: {", ".join(valid_roles)}')
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


# ============ 权限装饰器 ============

def require_auth(*roles: UserRole):
    """权限验证装饰器

    Args:
        *roles: 允许的角色列表，如果为空则只要求登录
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求头获取 token
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=401, detail="无法获取请求信息")

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="未提供认证令牌")

            token = auth_header.split(" ")[1]
            payload = auth_manager.verify_token(token)

            if not payload:
                raise HTTPException(status_code=401, detail="令牌无效或已过期")

            user_id = payload.get("sub")
            user = auth_manager.get_user_by_id(user_id)

            if not user:
                raise HTTPException(status_code=401, detail="用户不存在")

            if not user.is_active:
                raise HTTPException(status_code=403, detail="用户账户已被禁用")

            # 检查角色权限
            if roles and user.role not in roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"需要以下角色之一: {', '.join([r.value for r in roles])}"
                )

            # 将用户信息添加到 kwargs
            kwargs['current_user'] = user

            return await func(*args, **kwargs)
        return wrapper
    return decorator


app = FastAPI(
    title="SynergyAI API",
    description="""
    ## 多智能体协作系统 API

    SynergyAI 是一个强大的多智能体协作平台，让 AI 智能体协同工作以完成复杂任务。

    ### 主要功能

    * 🤖 **多角色智能体**：支持 HR、PM、BA、Dev、QA、Architect 等多个角色
    * 💬 **实时通信**：基于 WebSocket 的实时消息推送
    * 📋 **任务管理**：完整的任务创建、更新、追踪流程
    * 🎯 **智能编排**：自动协调不同角色的智能体协作
    * ⚙️ **灵活配置**：支持多种 LLM 提供商和模型配置

    ### 支持的 LLM 提供商

    * OpenAI (GPT-4, GPT-4o, etc.)
    * Anthropic (Claude 系列)
    * 智谱 AI (GLM 系列)
    * 自定义端点

    ### 快速开始

    1. 创建会话：`POST /api/session`
    2. 配置模型：`POST /api/config`
    3. 开始聊天：`POST /api/chat` 或使用 WebSocket `/ws/chat`

    ### 文档

    * Swagger UI: `/docs`
    * ReDoc: `/redoc`
    * OpenAPI JSON: `/openapi.json`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "SynergyAI Team",
        "email": "support@synergyai.com",
    },
    license_info={
        "name": "MIT License",
    },
    tags=[
        {
            "name": "auth",
            "description": "用户认证相关接口"
        },
        {
            "name": "session",
            "description": "会话管理相关接口"
        },
        {
            "name": "chat",
            "description": "聊天和消息相关接口"
        },
        {
            "name": "tasks",
            "description": "任务管理相关接口"
        },
        {
            "name": "config",
            "description": "模型配置相关接口"
        },
        {
            "name": "agents",
            "description": "智能体相关接口"
        },
        {
            "name": "websocket",
            "description": "WebSocket 实时通信"
        },
        {
            "name": "health",
            "description": "健康检查和系统状态"
        }
    ]
)


# ============ CORS 配置 ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)


# ============ 性能监控中间件 ============

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算处理时间
    process_time = time.time() - start_time

    # 记录性能数据
    path = request.url.path
    status_code = response.status_code
    perf_monitor.record_request(path, process_time, status_code)

    # 添加响应头
    response.headers["X-Process-Time"] = str(process_time)

    # 慢请求日志
    if process_time > perf_monitor.slow_threshold:
        logger.warning(f"Slow request: {path} took {process_time:.3f}s")

    return response


templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

storage = Storage()
orchestrator: Optional[MultiAgentOrchestrator] = None
current_session: Optional[Session] = None
session_creation_lock = asyncio.Lock()


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
    """优化的 WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_count = 0
        self.message_queue = asyncio.Queue()  # 消息队列
        self.broadcast_task = None  # 广播任务

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_count += 1
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

        # 启动消息处理任务（如果还没启动）
        if self.broadcast_task is None:
            self.broadcast_task = asyncio.create_task(self._process_message_queue())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息（优化：使用异常处理和超时）"""
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Send personal message timeout")
        except Exception as e:
            logger.warning(f"Failed to send personal message: {e}")

    async def broadcast(self, message: dict):
        """广播消息（优化：使用消息队列批量发送）"""
        await self.message_queue.put(("broadcast", message, None))

    async def _process_message_queue(self):
        """处理消息队列（批量发送优化）"""
        while True:
            try:
                # 批量处理消息（最多100ms等待或10条消息）
                messages = []
                for _ in range(10):
                    try:
                        msg = await asyncio.wait_for(
                            self.message_queue.get(),
                            timeout=0.1
                        )
                        messages.append(msg)
                    except asyncio.TimeoutError:
                        break

                if not messages:
                    continue

                # 批量发送消息
                for msg_type, message, websocket in messages:
                    if msg_type == "broadcast":
                        await self._broadcast_now(message)
                    elif msg_type == "personal" and websocket:
                        await self.send_personal_message(message, websocket)

            except Exception as e:
                logger.error(f"Error processing message queue: {e}")

    async def _broadcast_now(self, message: dict):
        """立即广播消息（优化：并发发送）"""
        if not self.active_connections:
            return

        # 并发发送所有消息
        tasks = []
        for connection in self.active_connections:
            tasks.append(self._safe_send(connection, message))

        # 等待所有发送完成（忽略失败）
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send(self, websocket: WebSocket, message: dict):
        """安全发送消息（带异常处理）"""
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=5.0)
        except Exception as e:
            logger.debug(f"Failed to send to websocket: {e}")
            # 发送失败时，移除连接
            self.disconnect(websocket)


manager = ConnectionManager()


class ChatRequest(BaseModel):
    """聊天请求模型

    用于向智能体发送消息的请求模型
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "message": "请帮我设计一个用户认证系统",
                "model": "gpt-4o",
                "api_key": "sk-xxx",
                "base_url": "https://api.openai.com/v1"
            }
        }


class TaskCreate(BaseModel):
    """任务创建模型

    用于创建新任务的请求模型
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "title": "实现用户登录功能",
                "description": "包括用户注册、登录、密码重置等功能",
                "assignee": "dev-1",
                "assignee_role": "dev",
                "priority": "high"
            }
        }


class TaskUpdate(BaseModel):
    """任务更新模型

    用于更新现有任务的请求模型
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "state": "in_progress",
                "priority": "high",
                "notes": ["正在开发中", "预计本周完成"]
            }
        }


class ConfigRequest(BaseModel):
    """默认模型配置请求

    用于配置系统默认的 LLM 模型
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model": "gpt-4o",
                "api_key": "sk-xxx",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7
            }
        }


class AgentConfigRequest(BaseModel):
    """智能体模型配置请求

    为特定角色的智能体配置 LLM 模型
    """
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

    class Config:
        json_schema_extra = {
            "example": {
                "role": "dev",
                "provider": "openai",
                "model": "gpt-4o",
                "api_key": "sk-xxx",
                "temperature": 0.7
            }
        }


class BatchConfigRequest(BaseModel):
    """批量智能体配置请求

    批量为多个智能体角色配置模型
    """
    configs: List[AgentConfigRequest]

    class Config:
        json_schema_extra = {
            "example": {
                "configs": [
                    {
                        "role": "dev",
                        "provider": "openai",
                        "model": "gpt-4o"
                    },
                    {
                        "role": "qa",
                        "provider": "openai",
                        "model": "gpt-4o"
                    }
                ]
            }
        }


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


@app.get("/login", response_class=HTMLResponse, tags=["ui"], summary="登录页面", description="用户登录注册页面")
@log_request
async def login_page(request: Request):
    """返回登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/", response_class=HTMLResponse, tags=["health"])
@log_request
async def index(request: Request):
    """返回主页 HTML

    访问系统主页，返回单页应用界面
    """
    logger.info("Index page accessed")
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/config", tags=["config"], summary="配置默认模型", description="设置系统默认的 LLM 提供商和模型")
@log_request
async def configure(req: ConfigRequest):
    """配置默认 LLM 模型

    设置系统使用的默认 LLM 提供商和模型配置，该配置将应用于所有未单独配置的智能体。

    - **provider**: LLM 提供商 (openai, anthropic, zhipu, custom)
    - **model**: 模型名称
    - **api_key**: API 密钥
    - **base_url**: API 基础 URL (可选)
    - **temperature**: 温度参数 (0-1)
    """
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

        # 清除配置缓存
        await cache_manager.delete("config:all")

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


@app.post("/api/config/agent", tags=["config"], summary="配置智能体模型", description="为特定角色的智能体配置专用的 LLM 模型")
async def configure_agent(req: AgentConfigRequest):
    """配置智能体专用模型

    为特定角色的智能体配置独立的 LLM 模型，使其使用与其他角色不同的模型配置。

    - **role**: 智能体角色 (hr, pm, ba, dev, qa, architect)
    - **provider**: LLM 提供商
    - **model**: 模型名称
    - **api_key**: API 密钥
    - **base_url**: API 基础 URL (可选)
    - **temperature**: 温度参数
    """
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


@app.post("/api/config/agents", tags=["config"], summary="批量配置智能体", description="一次性为多个智能体角色配置模型")
async def configure_agents(req: BatchConfigRequest):
    """批量配置智能体模型

    一次性为多个智能体角色配置 LLM 模型，提高配置效率。

    - **configs**: 智能体配置列表
    """
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


@app.get("/api/config", tags=["config"], summary="获取模型配置", description="获取当前所有智能体的模型配置信息")
async def get_config():
    """获取当前配置

    返回当前系统默认模型配置以及所有智能体角色的配置信息。
    """
    # 尝试从缓存获取
    cache_key = "config:all"
    cached_config = await cache_manager.get(cache_key)
    if cached_config is not None:
        return cached_config

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

        result = {
            "default": default_response,
            "agents": agent_configs,
            "providers": list(MODEL_OPTIONS.keys()),
            "models": MODEL_OPTIONS
        }

        # 缓存结果（5分钟）
        await cache_manager.set(cache_key, result, ttl=300)

        return result
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
    """WebSocket 聊天端点

    建立实时双向通信连接，用于发送消息和接收智能体响应。

    **支持的消息类型:**
    - `chat`: 发送聊天消息
    - `create_session`: 创建新会话
    - `typing`: 显示正在输入状态
    - `ping`: 心跳检测

    **服务器响应类型:**
    - `connected`: 连接成功
    - `message`: 聊天消息
    - `session_created`: 会话创建成功
    - `session_end`: 会话结束
    - `typing`: 正在输入
    - `error`: 错误信息
    """
    try:
        await manager.connect(websocket)
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket连接成功"
        })
        logger.info("WebSocket connection established")

        while True:
            try:
                data = await websocket.receive_json()
                await handle_websocket_message(data, websocket)
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"处理消息失败: {str(e)}"
                })
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during connection")
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}", exc_info=True)
    finally:
        manager.disconnect(websocket)
        logger.info("WebSocket connection closed")


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
        async with session_creation_lock:
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


@app.post("/api/session", tags=["session"], summary="创建会话", description="创建新的协作会话（项目）")
@log_request
async def create_session():
    """创建新会话

    创建一个新的协作会话，用于管理一个独立的项目或任务。
    返回会话 ID，用于后续的消息发送和任务管理。
    """
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


@app.get("/api/session", tags=["session"], summary="获取当前会话", description="获取当前活跃会话的信息")
@log_request
async def get_session():
    """获取当前会话

    返回当前活跃会话的基本信息，包括会话 ID、轮次等。
    如果没有活跃会话，返回 active: false
    """
    if not current_session:
        return {"active": False}

    return {
        "active": current_session.is_active,
        "session_id": current_session.id,
        "turn_count": current_session.turn_count,
        "created_at": current_session.created_at.isoformat()
    }


@app.get("/api/sessions", tags=["session"], summary="列出所有会话", description="获取系统中所有历史会话列表")
@log_request
async def list_sessions():
    """列出所有会话

    返回系统中所有保存的会话列表，包括会话 ID、创建时间等信息。
    """
    sessions = storage.list_sessions()
    return {"sessions": sessions}


@app.post("/api/sessions/{session_id}/load", tags=["session"], summary="加载会话", description="加载指定的历史会话")
@log_request
async def load_session(session_id: str):
    """加载会话

    从存储中加载指定的历史会话，使其成为当前活跃会话。
    可以继续之前的对话和任务。

    - **session_id**: 要加载的会话 ID
    """
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


@app.get("/api/messages", tags=["chat"], summary="获取消息历史", description="获取当前会话的所有消息记录")
@log_request
async def get_messages():
    """获取消息历史

    返回当前会话中的所有消息，包括用户消息和所有智能体的响应。
    """
    if not current_session:
        return {"messages": []}

    return {
        "messages": [msg.to_dict() for msg in current_session.messages],
        "turn_count": current_session.turn_count
    }


@app.post("/api/chat", tags=["chat"], summary="发送聊天消息", description="向智能体发送消息并获取响应")
@log_request
async def chat(req: ChatRequest):
    """发送聊天消息

    向智能体发送消息，获取响应。支持多智能体协作对话。

    - **message**: 要发送的消息内容 (1-10000 字符)
    - **model**: 使用的模型 (可选，默认 gpt-4)
    - **api_key**: API 密钥 (可选)
    - **base_url**: API 基础 URL (可选)
    """
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


@app.get("/api/tasks", tags=["tasks"], summary="获取任务列表", description="获取当前会话的所有任务")
@log_request
async def get_tasks():
    """获取任务列表

    返回当前会话中创建的所有任务及其状态。
    """
    if not current_session:
        return {"tasks": []}

    return {
        "tasks": [task.to_dict() for task in current_session.tasks.values()]
    }


@app.post("/api/tasks", tags=["tasks"], summary="创建任务", description="创建新任务")
@log_request
async def create_task(task: TaskCreate):
    """创建新任务

    在当前会话中创建一个新任务。

    - **title**: 任务标题 (必填，1-200 字符)
    - **description**: 任务描述 (可选)
    - **assignee**: 负责人 (可选)
    - **assignee_role**: 负责人角色 (可选: hr, pm, ba, dev, qa, architect)
    - **priority**: 优先级 (可选: low, medium, high，默认 medium)
    """
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


@app.put("/api/tasks/{task_id}", tags=["tasks"], summary="更新任务", description="更新现有任务的信息")
@log_request
async def update_task(task_id: str, task_update: TaskUpdate):
    """更新任务

    更新指定任务的信息。支持部分更新，只更新提供的字段。

    - **task_id**: 任务 ID (路径参数)
    - **title**: 新的标题 (可选)
    - **description**: 新的描述 (可选)
    - **assignee**: 新的负责人 (可选)
    - **assignee_role**: 新的负责人角色 (可选)
    - **state**: 新的状态 (可选: pending, in_progress, review, done, blocked)
    - **priority**: 新的优先级 (可选: low, medium, high)
    - **notes**: 备注列表 (可选)
    """
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


@app.delete("/api/tasks/{task_id}", tags=["tasks"], summary="删除任务", description="删除指定的任务")
@log_request
async def delete_task(task_id: str):
    """删除任务

    从当前会话中删除指定的任务。此操作不可撤销。

    - **task_id**: 要删除的任务 ID
    """
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


@app.get("/api/agents", tags=["agents"], summary="获取智能体列表", description="获取所有可用的智能体角色")
@log_request
async def get_agents():
    """获取智能体列表

    返回系统中所有可用的智能体角色及其描述。
    """
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


@app.get("/api/handover", tags=["chat"], summary="获取交接文档", description="获取会话结束时生成的交接文档")
@log_request
async def get_handover():
    """获取交接文档

    返回当前会话结束时的交接文档（如果有的话）。
    交接文档包含项目总结、任务状态、重要决策等信息。
    """
    if not current_session or not current_session.handover_doc:
        return {"handover": None}

    return {"handover": current_session.handover_doc}


# ============ 认证相关端点 ============

@app.post("/api/auth/register", tags=["auth"], summary="用户注册", description="注册新用户")
@log_request
async def register(user_data: UserRegister):
    """用户注册

    创建新用户账户。

    - **username**: 用户名 (3-50个字符)
    - **email**: 邮箱地址
    - **password**: 密码 (至少6个字符)
    - **role**: 角色 (admin/user/guest，默认为user)
    """
    try:
        # 检查用户名是否已存在
        existing_user = auth_manager.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = auth_manager.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被使用")

        # 创建用户
        user = auth_manager.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=UserRole(user_data.role)
        )

        logger.info(f"New user registered: {user.username}")

        return {
            "message": "注册成功",
            "user": user.to_dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="注册失败")


@app.post("/api/auth/login", tags=["auth"], summary="用户登录", description="用户登录获取访问令牌")
@log_request
async def login(login_data: UserLogin):
    """用户登录

    使用用户名和密码登录，成功返回JWT访问令牌。

    - **username**: 用户名
    - **password**: 密码

    返回的access_token需要在后续请求中通过Authorization头发送：
    Authorization: Bearer <access_token>
    """
    try:
        # 验证用户凭据
        user = auth_manager.authenticate(login_data.username, login_data.password)

        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 创建访问令牌
        access_token = auth_manager.create_access_token(user)

        logger.info(f"User logged in: {user.username}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="登录失败")


@app.get("/api/auth/me", tags=["auth"], summary="获取当前用户信息", description="获取当前登录用户的信息")
@log_request
async def get_current_user(request: Request):
    """获取当前用户信息

    返回当前登录用户的详细信息。
    需要在请求头中提供有效的JWT令牌。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token = auth_header.split(" ")[1]
    payload = auth_manager.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    user_id = payload.get("sub")
    user = auth_manager.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user.to_dict()


@app.put("/api/auth/me", tags=["auth"], summary="更新当前用户信息", description="更新当前登录用户的信息")
@log_request
async def update_current_user(
    request: Request,
    email: Optional[str] = None,
    password: Optional[str] = None
):
    """更新当前用户信息

    更新当前登录用户的邮箱或密码。
    需要在请求头中提供有效的JWT令牌。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token = auth_header.split(" ")[1]
    payload = auth_manager.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    user_id = payload.get("sub")
    user = auth_manager.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 这里可以添加更新用户信息的逻辑
    # 由于当前的AuthManager没有实现更新方法，暂时返回成功消息
    return {"message": "用户信息更新功能待实现"}


@app.get("/api/auth/users", tags=["auth"], summary="获取用户列表", description="获取所有用户列表（需要管理员权限）")
@log_request
async def list_users(request: Request):
    """获取用户列表

    返回系统中所有用户的列表。
    需要管理员权限。
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token = auth_header.split(" ")[1]
    payload = auth_manager.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    user_id = payload.get("sub")
    current_user = auth_manager.get_user_by_id(user_id)

    if not current_user or current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    users = auth_manager.list_users()
    return {
        "users": [user.to_dict() for user in users],
        "total": len(users)
    }


@app.get("/api/health", tags=["health"], summary="健康检查", description="检查系统运行状态")
async def health_check():
    """健康检查

    返回系统当前的运行状态，包括版本信息、活跃连接数等。
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "connections": len(manager.active_connections)
    }


@app.get("/api/performance", tags=["health"], summary="性能统计", description="获取系统性能统计数据")
async def get_performance_stats():
    """性能统计

    返回系统性能统计数据，包括请求计数、响应时间、慢请求等。
    """
    return perf_monitor.get_stats()


# ============ Feature List API ============

from core.features import FeatureList, Feature, FeatureStatus, FeaturePriority

# Initialize feature list
feature_list = FeatureList()


@app.get("/api/features", tags=["features"], summary="获取功能清单", description="获取所有功能列表")
async def get_features(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_role: Optional[str] = None
):
    """获取功能清单

    支持按状态、类别、优先级、负责人筛选
    """
    features = list(feature_list.features.values())

    # Filter by status
    if status:
        features = [f for f in features if f.status == status]

    # Filter by category
    if category:
        features = [f for f in features if f.category == category]

    # Filter by priority
    if priority:
        features = [f for f in features if f.priority == priority]

    # Filter by assignee_role
    if assignee_role:
        features = [f for f in features if f.assignee_role == assignee_role]

    return {
        "features": [f.to_dict() for f in features],
        "total": len(features)
    }


@app.get("/api/features/statistics", tags=["features"], summary="获取功能统计", description="获取功能清单统计信息")
async def get_feature_statistics():
    """获取功能统计

    返回功能清单的统计数据，包括完成进度、按状态/优先级/类别分布等。
    """
    return feature_list.get_statistics()


@app.get("/api/features/summary", tags=["features"], summary="获取功能进度摘要", description="获取功能清单进度摘要")
async def get_feature_summary():
    """获取功能进度摘要

    返回功能清单的文本格式进度摘要。
    """
    return {
        "summary": feature_list.get_progress_summary()
    }


@app.get("/api/features/report", tags=["features"], summary="获取功能报告", description="获取完整的功能清单报告")
async def get_feature_report():
    """获取功能报告

    返回完整的功能清单报告。
    """
    return {
        "report": feature_list.generate_report()
    }


@app.get("/api/features/next", tags=["features"], summary="获取下一个待办功能", description="获取下一个待处理的功能")
async def get_next_feature(assignee_role: Optional[str] = None):
    """获取下一个待办功能

    返回优先级最高的待处理功能。
    """
    feature = feature_list.get_next_feature(assignee_role)

    if not feature:
        raise HTTPException(status_code=404, detail="没有待处理的功能")

    return feature.to_dict()


@app.get("/api/features/pending", tags=["features"], summary="获取待办功能列表", description="获取待处理功能列表")
async def get_pending_features(limit: int = 10):
    """获取待办功能列表

    返回指定数量的待处理功能。
    """
    features = feature_list.get_pending_features(limit)

    return {
        "features": [f.to_dict() for f in features],
        "total": len(features)
    }


@app.put("/api/features/{feature_id}/status", tags=["features"], summary="更新功能状态", description="更新功能状态")
async def update_feature_status(feature_id: str, status: str):
    """更新功能状态

    更新指定功能的状态。
    """
    if status not in [s.value for s in FeatureStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"无效的状态值。可选值: {', '.join([s.value for s in FeatureStatus])}"
        )

    if feature_id not in feature_list.features:
        raise HTTPException(status_code=404, detail=f"功能 {feature_id} 不存在")

    feature_list.update_feature_status(feature_id, status)

    return {
        "message": f"功能 {feature_id} 状态已更新为 {status}",
        "feature": feature_list.features[feature_id].to_dict()
    }


@app.post("/api/features", tags=["features"], summary="添加新功能", description="添加新功能到清单")
async def add_feature(
    id: str,
    category: str,
    priority: str,
    title: str,
    description: str,
    assignee_role: str,
    steps: List[str],
    notes: str = ""
):
    """添加新功能

    添加新功能到功能清单。
    """
    # Validate inputs
    if id in feature_list.features:
        raise HTTPException(status_code=400, detail=f"功能 ID {id} 已存在")

    if priority not in [p.value for p in FeaturePriority]:
        raise HTTPException(
            status_code=400,
            detail=f"无效的优先级。可选值: {', '.join([p.value for p in FeaturePriority])}"
        )

    if assignee_role not in [r.value for r in AgentRole]:
        raise HTTPException(
            status_code=400,
            detail=f"无效的角色。可选值: {', '.join([r.value for r in AgentRole])}"
        )

    # Create feature
    feature = Feature(
        id=id,
        category=category,
        priority=priority,
        title=title,
        description=description,
        status=FeatureStatus.PENDING.value,
        assignee_role=assignee_role,
        steps=steps,
        passes=False,
        notes=notes
    )

    feature_list.add_feature(feature)

    return {
        "message": f"功能 {title} 已添加",
        "feature": feature.to_dict()
    }


@app.get("/api/features/{feature_id}", tags=["features"], summary="获取功能详情", description="获取指定功能的详细信息")
async def get_feature(feature_id: str):
    """获取功能详情

    返回指定功能的详细信息。
    """
    if feature_id not in feature_list.features:
        raise HTTPException(status_code=404, detail=f"功能 {feature_id} 不存在")

    return feature_list.features[feature_id].to_dict()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
