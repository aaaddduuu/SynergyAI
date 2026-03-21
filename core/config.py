"""配置管理模块

集中管理应用程序配置，包括安全设置
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    app_name: str = "SynergyAI"
    version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")

    # 安全配置
    secret_key: str = Field(default="", alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24小时

    # CORS 配置
    cors_origins: List[str] = Field(
        default=["http://localhost:8000", "http://localhost:3000"],
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    cors_expose_headers: List[str] = ["X-CSRF-Token", "X-RateLimit-*"]

    # Rate Limiting 配置
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, alias="RATE_LIMIT_PER_HOUR")

    # CSRF 配置
    csrf_enabled: bool = Field(default=True, alias="CSRF_ENABLED")
    csrf_token_expiry: int = 3600  # 1小时

    # 输入验证配置
    max_input_length: int = 10000
    enable_input_validation: bool = Field(default=True, alias="ENABLE_INPUT_VALIDATION")

    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    security_log_file: str = "logs/security.log"

    # 数据库配置
    database_url: str = Field(default="sqlite:///./data/synergyai.db", alias="DATABASE_URL")

    # JWT 配置
    jwt_secret_key: str = Field(default="", alias="JWT_SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True


settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
