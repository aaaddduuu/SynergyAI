"""用户认证和授权模块

实现用户注册、登录、JWT token管理等功能
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import json
from pathlib import Path


class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class User:
    """用户数据模型"""
    id: str
    username: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    def to_dict(self, include_sensitive=False):
        """转换为字典（排除敏感信息）"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
        if self.last_login:
            data["last_login"] = self.last_login.isoformat()
        if include_sensitive:
            data["hashed_password"] = self.hashed_password
        return data

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return self.hashed_password == hash_password(password)


def hash_password(password: str) -> str:
    """哈希密码（使用 SHA-256 + salt）"""
    salt = "ai-coworker-salt"  # 在生产环境中应该使用随机salt
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


class AuthManager:
    """认证管理器"""

    def __init__(self, db_path: str = "data/users.db", secret_key: str = None):
        self.db_path = db_path
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry_hours = 24

        # 确保数据库目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)

        conn.commit()
        conn.close()

    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """创建新用户"""
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user.id, user.username, user.email, user.hashed_password, user.role.value,
                  1 if user.is_active else 0, user.created_at.isoformat()))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.close()
            if "username" in str(e):
                raise ValueError("用户名已存在")
            elif "email" in str(e):
                raise ValueError("邮箱已被使用")
            raise

        conn.close()
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_user(row)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_user(row)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """通过ID获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_user(row)

    def _row_to_user(self, row) -> User:
        """将数据库行转换为User对象"""
        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            hashed_password=row[3],
            role=UserRole(row[4]),
            is_active=bool(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            last_login=datetime.fromisoformat(row[7]) if row[7] else None
        )

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = self.get_user_by_username(username)
        if not user:
            return None

        if not user.is_active:
            raise ValueError("用户账户已被禁用")

        if not user.verify_password(password):
            return None

        # 更新最后登录时间
        self._update_last_login(user.id)
        user.last_login = datetime.now()

        return user

    def _update_last_login(self, user_id: str):
        """更新用户最后登录时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
        conn.close()

    def create_access_token(self, user: User) -> str:
        """创建JWT访问令牌"""
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def list_users(self) -> List[User]:
        """获取所有用户列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_user(row) for row in rows]

    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """更新用户角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role.value, user_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def toggle_user_active(self, user_id: str) -> bool:
        """切换用户激活状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        new_status = not bool(row[0])
        cursor.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (1 if new_status else 0, user_id)
        )
        conn.commit()
        conn.close()

        return True


# 全局认证管理器实例
auth_manager = AuthManager()
