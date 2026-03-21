"""Pydantic 模型定义

包含所有请求/响应模型，提供输入验证
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============ 通用模型 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """成功响应"""
    message: str
    data: Optional[Any] = None


# ============ 认证相关模型 ============

class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., pattern=r'^[\w\.\+\-]+@[\w\.-]+\.\w+$', description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    @validator('username')
    def validate_username(cls, v):
        """验证用户名不包含特殊字符"""
        import re
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @validator('password')
    def validate_password(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ 消息和聊天相关模型 ============

class ChatMessage(BaseModel):
    """聊天消息"""
    content: str = Field(..., min_length=1, max_length=10000, description="消息内容")
    session_id: Optional[str] = Field(None, description="会话ID")

    @validator('content')
    def validate_content(cls, v):
        """验证消息内容"""
        from core.security import validator
        validator.validate_input(v, "message_content")
        return v


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    role: str
    content: str
    timestamp: str
    task_id: Optional[str] = None

    class Config:
        orm_mode = True


# ============ 任务相关模型 ============

class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, max_length=5000, description="任务描述")
    assignee: Optional[str] = Field(None, description="分配给的角色")
    priority: Optional[str] = Field("medium", pattern=r'^(low|medium|high)$', description="优先级")

    @validator('title')
    def validate_title(cls, v):
        """验证标题"""
        from core.security import validator
        validator.validate_input(v, "task_title")
        return v

    @validator('description')
    def validate_description(cls, v):
        """验证描述"""
        if v:
            from core.security import validator
            validator.validate_input(v, "task_description")
        return v


class TaskUpdateRequest(BaseModel):
    """更新任务请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = Field(None, pattern=r'^(pending|in_progress|completed|failed)$')
    assignee: Optional[str] = None
    priority: Optional[str] = Field(None, pattern=r'^(low|medium|high)$')

    @validator('title')
    def validate_title(cls, v):
        """验证标题"""
        if v:
            from core.security import validator
            validator.validate_input(v, "task_title")
        return v


# ============ 团队和项目相关模型 ============

class TeamCreateRequest(BaseModel):
    """创建团队请求"""
    name: str = Field(..., min_length=1, max_length=100, description="团队名称")
    description: Optional[str] = Field(None, max_length=500, description="团队描述")

    @validator('name')
    def validate_name(cls, v):
        """验证名称"""
        from core.security import validator
        validator.validate_input(v, "team_name")
        return v


class TeamUpdateRequest(BaseModel):
    """更新团队请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectCreateRequest(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")
    team_id: str = Field(..., description="团队ID")

    @validator('name')
    def validate_name(cls, v):
        """验证名称"""
        from core.security import validator
        validator.validate_input(v, "project_name")
        return v


# ============ 插件相关模型 ============

class AgentRoleEnum(str, Enum):
    """智能体角色枚举"""
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    DEV = "dev"
    QA = "qa"


class PluginCreateRequest(BaseModel):
    """创建插件请求"""
    name: str = Field(..., min_length=1, max_length=100, description="插件名称")
    description: str = Field(..., max_length=500, description="插件描述")
    role: AgentRoleEnum = Field(..., description="智能体角色")
    system_prompt: str = Field(..., min_length=10, max_length=5000, description="系统提示词")
    capabilities: List[str] = Field(default_factory=list, description="能力列表")

    @validator('name')
    def validate_name(cls, v):
        """验证名称"""
        from core.security import validator
        validator.validate_input(v, "plugin_name")
        return v

    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        """验证系统提示词"""
        from core.security import validator
        validator.validate_input(v, "system_prompt")
        return v


class PluginUpdateRequest(BaseModel):
    """更新插件请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    system_prompt: Optional[str] = Field(None, min_length=10, max_length=5000)
    capabilities: Optional[List[str]] = None
    is_active: Optional[bool] = None


# ============ 功能清单相关模型 ============

class FeatureUpdateStatusRequest(BaseModel):
    """更新功能状态请求"""
    status: str = Field(..., pattern=r'^(pending|in_progress|review|done)$')


class FeatureCreateRequest(BaseModel):
    """创建功能请求"""
    id: str = Field(..., min_length=1, max_length=50, description="功能ID")
    category: str = Field(..., description="功能类别")
    priority: str = Field(..., pattern=r'^(low|medium|high)$', description="优先级")
    title: str = Field(..., min_length=1, max_length=100, description="功能标题")
    description: str = Field(..., min_length=1, max_length=500, description="功能描述")
    assignee_role: str = Field(..., description="负责人角色")
    steps: List[str] = Field(..., min_items=1, description="任务步骤")
    notes: Optional[str] = Field(None, max_length=1000, description="注意事项")
