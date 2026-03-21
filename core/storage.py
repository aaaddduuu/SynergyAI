import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
from pathlib import Path
from contextlib import contextmanager
import threading


class TeamRole(str, Enum):
    """团队成员角色"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class TaskState(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class AgentRole(str, Enum):
    HR = "hr"
    PM = "pm"
    BA = "ba"
    DEV = "dev"
    QA = "qa"
    ARCHITECT = "architect"
    ORCHESTRATOR = "orchestrator"


class MessageType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TASK_UPDATE = "task_update"
    REQUEST = "request"


@dataclass
class Message:
    id: str
    sender: str
    sender_role: str
    content: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "sender_role": self.sender_role,
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class Task:
    id: str
    title: str
    description: str
    assignee: Optional[str] = None
    assignee_role: Optional[AgentRole] = None
    state: TaskState = TaskState.PENDING
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    priority: str = "medium"
    dependencies: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "assignee": self.assignee,
            "assignee_role": self.assignee_role.value if self.assignee_role else None,
            "state": self.state.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "priority": self.priority,
            "dependencies": self.dependencies,
            "notes": self.notes
        }


@dataclass
class Agent:
    id: str
    name: str
    role: AgentRole
    description: str
    system_prompt: str
    is_active: bool = True
    current_task_id: Optional[str] = None
    message_count: int = 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "is_active": self.is_active,
            "current_task_id": self.current_task_id,
            "message_count": self.message_count
        }


@dataclass
class TeamMember:
    """团队成员"""
    user_id: str
    username: str
    role: TeamRole
    joined_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat()
        }


@dataclass
class Team:
    """团队数据模型"""
    id: str
    name: str
    description: str
    owner_id: str
    members: Dict[str, TeamMember] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "members": {k: v.to_dict() for k, v in self.members.items()},
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }


@dataclass
class Project:
    """项目数据模型（相当于 Session）"""
    id: str
    team_id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def to_dict(self):
        return {
            "id": self.id,
            "team_id": self.team_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }


class Session:
    def __init__(self, id: Optional[str] = None, team_id: Optional[str] = None, project_id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.team_id = team_id
        self.project_id = project_id
        self.messages: List[Message] = []
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.created_at = datetime.now()
        self.turn_count = 0
        self.is_active = True
        self.handover_doc: Optional[str] = None
        self._progress_log_path: Optional[Path] = None

    def _get_progress_log_path(self) -> Path:
        """获取进度日志文件路径"""
        if self._progress_log_path is None:
            log_dir = Path("data/sessions") / self.id
            log_dir.mkdir(parents=True, exist_ok=True)
            self._progress_log_path = log_dir / "progress.txt"
        return self._progress_log_path

    def add_message(self, message: Message):
        self.messages.append(message)
        if message.message_type == MessageType.USER or message.message_type == MessageType.AGENT:
            self.turn_count += 1

    def check_session_end(self) -> tuple[bool, str]:
        """Check if session should end. Returns (should_end, reason)"""
        if self.turn_count >= 30:
            return True, "conversation_30_turns"

        for task in self.tasks.values():
            if task.state == TaskState.DONE:
                return True, "task_completed"

        return False, ""

    def update_progress_log(self, agent_role: str, work_done: str, additional_info: Optional[dict] = None):
        """
        记录每次 Agent 会话的进展到进度日志

        Args:
            agent_role: Agent 角色（如 dev, qa, pm 等）
            work_done: 完成的工作描述
            additional_info: 额外信息（如修改的文件、创建的任务等）
        """
        try:
            progress_file = self._get_progress_log_path()

            # 统计任务状态
            completed_tasks = [t for t in self.tasks.values() if t.state == TaskState.DONE]
            pending_tasks = [t for t in self.tasks.values() if t.state != TaskState.DONE]
            in_progress_tasks = [t for t in self.tasks.values() if t.state == TaskState.IN_PROGRESS]

            # 构建日志条目
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"""
## {timestamp} - {agent_role.upper()} Agent

### 工作内容
{work_done}

### 任务状态
- 总任务数: {len(self.tasks)}
- 已完成: {len(completed_tasks)}
- 进行中: {len(in_progress_tasks)}
- 待处理: {len(pending_tasks)}

### 会话信息
- 对话轮次: {self.turn_count}/30
- 消息数量: {len(self.messages)}
"""

            # 添加额外信息
            if additional_info:
                log_entry += "\n### 额外信息\n"
                for key, value in additional_info.items():
                    log_entry += f"- {key}: {value}\n"

            # 添加待办任务列表（便于快速了解下一步工作）
            if pending_tasks:
                log_entry += "\n### 待办任务\n"
                for task in sorted(pending_tasks, key=lambda t: (
                    0 if t.state == TaskState.IN_PROGRESS else 1,  # 进行中的排前面
                    t.priority  # 然后按优先级
                )):
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
                    state_icon = {"in_progress": "▶️", "pending": "⏸️", "review": "👀"}.get(task.state.value, "❓")
                    log_entry += f"{priority_icon} {state_icon} **{task.title}** (负责人: {task.assignee_role or '未分配'})\n"

            log_entry += "\n" + "-" * 80 + "\n"

            # 追加到日志文件
            with open(progress_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            # 记录失败不应该影响主流程
            print(f"Warning: Failed to write progress log: {e}")

    def get_progress_summary(self) -> str:
        """
        获取进度摘要，用于快速了解当前状态
        这解决了"上下文恢复困难"的问题
        """
        try:
            progress_file = self._get_progress_log_path()
            if progress_file.exists():
                with open(progress_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # 返回最后 2000 字符（最近的工作）
                if len(content) > 2000:
                    return "\n...[更早的工作记录已省略]...\n\n" + content[-2000:]
                return content
            return "暂无进度记录"
        except Exception as e:
            return f"无法读取进度记录: {e}"

    def generate_handover_doc(self) -> str:
        """Generate handover document for incomplete tasks"""
        incomplete_tasks = [t for t in self.tasks.values() if t.state != TaskState.DONE]

        doc = f"""# 离职交接文档
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Session ID: {self.id}

## 交接事项

### 未完成任务 ({len(incomplete_tasks)} 项)
"""
        for task in incomplete_tasks:
            doc += f"""
### {task.title}
- 描述: {task.description}
- 当前状态: {task.state.value}
- 负责人: {task.assignee or '未分配'}
- 优先级: {task.priority}
- 备注: {', '.join(task.notes) if task.notes else '无'}
"""

        doc += """
## 建议
1. PM需要申请额外人力
2. 交接给新成员继续跟进
"""
        return doc


class Storage:
    def __init__(self, db_path: str = "data/workspace.db"):
        self.db_path = db_path
        self._local = threading.local()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器（支持线程本地）"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0  # 10秒超时
            )
            # 启用 WAL 模式提高并发性能
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            # 优化其他 SQLite 参数
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=-64000")  # 64MB 缓存
            self._local.conn.execute("PRAGMA temp_store=MEMORY")

        yield self._local.conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 创建 teams 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TEXT
                )
            """)

            # 创建 projects 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    data TEXT,
                    created_at TEXT,
                    FOREIGN KEY (team_id) REFERENCES teams(id)
                )
            """)

            # 创建 sessions 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    team_id TEXT,
                    project_id TEXT,
                    data TEXT,
                    created_at TEXT,
                    FOREIGN KEY (team_id) REFERENCES teams(id),
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """)

            # 为常用查询字段添加索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_created_at
                ON sessions(created_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_team_id
                ON sessions(team_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_project_id
                ON sessions(project_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_team_id
                ON projects(team_id)
            """)

            conn.commit()

    def save_session(self, session: Session):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            session_data = {
                "id": session.id,
                "team_id": session.team_id,
                "project_id": session.project_id,
                "messages": [m.to_dict() for m in session.messages],
                "agents": {k: v.to_dict() for k, v in session.agents.items()},
                "tasks": {k: v.to_dict() for k, v in session.tasks.items()},
                "turn_count": session.turn_count,
                "is_active": session.is_active,
                "handover_doc": session.handover_doc
            }

            cursor.execute(
                "INSERT OR REPLACE INTO sessions (id, team_id, project_id, data, created_at) VALUES (?, ?, ?, ?, ?)",
                (session.id, session.team_id, session.project_id, json.dumps(session_data), session.created_at.isoformat())
            )

            conn.commit()

    def load_session(self, session_id: str) -> Optional[Session]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT data FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()

            if not row:
                return None

            data = json.loads(row[0])
            session = Session(data["id"], data.get("team_id"), data.get("project_id"))
            session.turn_count = data.get("turn_count", 0)
            session.is_active = data.get("is_active", True)
            session.handover_doc = data.get("handover_doc")

            for m in data.get("messages", []):
                msg = Message(
                    id=m["id"],
                    sender=m["sender"],
                    sender_role=m["sender_role"],
                    content=m["content"],
                    message_type=MessageType(m["message_type"]),
                    timestamp=datetime.fromisoformat(m["timestamp"]),
                    metadata=m.get("metadata", {})
                )
                session.messages.append(msg)

            for k, v in data.get("agents", {}).items():
                agent = Agent(
                    id=v["id"],
                    name=v["name"],
                    role=AgentRole(v["role"]),
                    description=v["description"],
                    system_prompt="",
                    is_active=v.get("is_active", True),
                    current_task_id=v.get("current_task_id"),
                    message_count=v.get("message_count", 0)
                )
                session.agents[k] = agent

            for k, v in data.get("tasks", {}).items():
                task = Task(
                    id=v["id"],
                    title=v["title"],
                    description=v["description"],
                    assignee=v.get("assignee"),
                    assignee_role=AgentRole(v["assignee_role"]) if v.get("assignee_role") else None,
                    state=TaskState(v["state"]),
                    created_by=v.get("created_by", ""),
                    priority=v.get("priority", "medium"),
                    notes=v.get("notes", [])
                )
                session.tasks[k] = task

            return session

    def list_sessions(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id, created_at FROM sessions ORDER BY created_at DESC")
            rows = cursor.fetchall()

            return [{"id": r[0], "created_at": r[1]} for r in rows]

    # ========== 团队管理方法 ==========

    def create_team(self, team: Team) -> bool:
        """创建新团队"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO teams (id, data, created_at) VALUES (?, ?, ?)",
                    (team.id, json.dumps(team.to_dict()), team.created_at.isoformat())
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_team(self, team_id: str) -> Optional[Team]:
        """获取团队信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT data FROM teams WHERE id = ?", (team_id,))
            row = cursor.fetchone()

            if not row:
                return None

            data = json.loads(row[0])
            members = {}
            for k, v in data.get("members", {}).items():
                members[k] = TeamMember(
                    user_id=v["user_id"],
                    username=v["username"],
                    role=TeamRole(v["role"]),
                    joined_at=datetime.fromisoformat(v["joined_at"])
                )

            return Team(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                owner_id=data["owner_id"],
                members=members,
                created_at=datetime.fromisoformat(data["created_at"]),
                is_active=data.get("is_active", True)
            )

    def list_teams(self) -> List[Team]:
        """获取所有团队列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT data FROM teams ORDER BY created_at DESC")
            rows = cursor.fetchall()

            teams = []
            for row in rows:
                data = json.loads(row[0])
                members = {}
                for k, v in data.get("members", {}).items():
                    members[k] = TeamMember(
                        user_id=v["user_id"],
                        username=v["username"],
                        role=TeamRole(v["role"]),
                        joined_at=datetime.fromisoformat(v["joined_at"])
                    )

                teams.append(Team(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    owner_id=data["owner_id"],
                    members=members,
                    created_at=datetime.fromisoformat(data["created_at"]),
                    is_active=data.get("is_active", True)
                ))

            return teams

    def update_team(self, team: Team) -> bool:
        """更新团队信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE teams SET data = ? WHERE id = ?",
                (json.dumps(team.to_dict()), team.id)
            )
            conn.commit()

            return cursor.rowcount > 0

    def delete_team(self, team_id: str) -> bool:
        """删除团队"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
            conn.commit()

            return cursor.rowcount > 0

    # ========== 项目管理方法 ==========

    def create_project(self, project: Project) -> bool:
        """创建新项目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO projects (id, team_id, data, created_at) VALUES (?, ?, ?, ?)",
                    (project.id, project.team_id, json.dumps(project.to_dict()), project.created_at.isoformat())
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT data FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()

            if not row:
                return None

            data = json.loads(row[0])
            return Project(
                id=data["id"],
                team_id=data["team_id"],
                name=data["name"],
                description=data["description"],
                owner_id=data["owner_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                is_active=data.get("is_active", True)
            )

    def list_projects(self, team_id: Optional[str] = None) -> List[Project]:
        """获取项目列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if team_id:
                cursor.execute(
                    "SELECT data FROM projects WHERE team_id = ? ORDER BY created_at DESC",
                    (team_id,)
                )
            else:
                cursor.execute("SELECT data FROM projects ORDER BY created_at DESC")

            rows = cursor.fetchall()

            projects = []
            for row in rows:
                data = json.loads(row[0])
                projects.append(Project(
                    id=data["id"],
                    team_id=data["team_id"],
                    name=data["name"],
                    description=data["description"],
                    owner_id=data["owner_id"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    is_active=data.get("is_active", True)
                ))

            return projects

    def update_project(self, project: Project) -> bool:
        """更新项目信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE projects SET data = ? WHERE id = ?",
                (json.dumps(project.to_dict()), project.id)
            )
            conn.commit()

            return cursor.rowcount > 0

    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()

            return cursor.rowcount > 0
