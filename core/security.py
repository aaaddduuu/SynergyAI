"""安全模块

提供系统安全增强功能：
- CSRF 保护
- 输入验证
- Rate Limiting
- 安全日志
"""

import os
import re
import hashlib
import time
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable, Any, Set
from functools import wraps
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("ai_coworker.security")


# ============ CSRF 保护 ============

class CSRFTokenManager:
    """CSRF Token 管理器"""

    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
        self.token_expiry = 3600  # 1小时
        self._tokens: Dict[str, float] = {}

    def generate_token(self, session_id: str) -> str:
        """生成 CSRF token"""
        # 使用 session_id + 时间戳 + secret_key 生成 token
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}:{self.secret_key}"
        token = hashlib.sha256(data.encode()).hexdigest()

        # 存储 token 及其过期时间
        self._tokens[token] = time.time() + self.token_expiry

        return token

    def validate_token(self, token: str, session_id: str) -> bool:
        """验证 CSRF token"""
        if not token or token not in self._tokens:
            return False

        # 检查是否过期
        if self._tokens[token] < time.time():
            del self._tokens[token]
            return False

        return True

    def cleanup_expired_tokens(self):
        """清理过期的 token"""
        current_time = time.time()
        expired = [t for t, exp in self._tokens.items() if exp < current_time]
        for token in expired:
            del self._tokens[token]


csrf_manager = CSRFTokenManager()


# ============ Rate Limiting ============

@dataclass
class RateLimitConfig:
    """Rate Limiting 配置"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # 突发流量限制


class RateLimiter:
    """Rate Limiter - 防止 DDoS 和暴力破解"""

    # Rate limiting 白名单路径
    WHITELIST = {
        "/api/auth/csrf-token",
        "/api/health",
        "/api/performance",
        "/api/features",
        "/login",
    }

    def __init__(self):
        # 存储每个 IP/用户的请求记录
        self._requests: Dict[str, List[float]] = defaultdict(list)
        # 配置
        self.configs: Dict[str, RateLimitConfig] = {
            "default": RateLimitConfig(),
            "auth": RateLimitConfig(requests_per_minute=5, requests_per_hour=20),  # 认证接口更严格
            "api": RateLimitConfig(requests_per_minute=30, requests_per_hour=500),
        }
        # 清理间隔（秒）
        self.cleanup_interval = 300  # 5分钟
        self._last_cleanup = time.time()

    def _is_whitelisted(self, path: str) -> bool:
        """检查路径是否在白名单中"""
        for whitelist_path in self.WHITELIST:
            if path.startswith(whitelist_path):
                return True
        return False

    def _get_key(self, request: Request) -> str:
        """获取限制键（IP 或用户 ID）"""
        # 优先使用用户 ID（如果已认证）
        user_id = request.state.user if hasattr(request.state, "user") else None
        if user_id:
            return f"user:{user_id}"

        # 否则使用 IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}"

    def _get_category(self, path: str) -> str:
        """根据路径获取限制类别"""
        if path.startswith("/api/auth"):
            return "auth"
        elif path.startswith("/api"):
            return "api"
        return "default"

    def _cleanup_old_requests(self):
        """清理旧的请求记录"""
        current_time = time.time()
        if current_time - self._last_cleanup < self.cleanup_interval:
            return

        cutoff_time = current_time - 3600  # 只保留最近1小时的记录
        for key in list(self._requests.keys()):
            # 过滤掉过期的请求时间
            self._requests[key] = [
                req_time for req_time in self._requests[key]
                if req_time > cutoff_time
            ]
            # 如果没有请求了，删除这个键
            if not self._requests[key]:
                del self._requests[key]

        self._last_cleanup = current_time

    def check_rate_limit(self, request: Request) -> tuple[bool, Optional[str]]:
        """检查是否超过 rate limit"""
        # 检查是否在白名单中
        if self._is_whitelisted(request.url.path):
            return True, None

        self._cleanup_old_requests()

        key = self._get_key(request)
        category = self._get_category(request.url.path)
        config = self.configs.get(category, self.configs["default"])

        current_time = time.time()
        request_times = self._requests[key]

        # 移除超过1分钟的请求
        request_times[:] = [t for t in request_times if current_time - t < 60]

        # 检查每分钟限制
        if len(request_times) >= config.requests_per_minute:
            logger.warning(f"Rate limit exceeded (minute): {key}")
            return False, f"Rate limit exceeded: {config.requests_per_minute} requests per minute"

        # 检查每小时限制
        hour_ago = current_time - 3600
        hour_requests = sum(1 for t in request_times if t > hour_ago)
        if hour_requests >= config.requests_per_hour:
            logger.warning(f"Rate limit exceeded (hour): {key}")
            return False, f"Rate limit exceeded: {config.requests_per_hour} requests per hour"

        # 记录本次请求
        request_times.append(current_time)
        return True, None

    def get_rate_limit_info(self, request: Request) -> Dict[str, int]:
        """获取 rate limit 信息（用于响应头）"""
        key = self._get_key(request)
        category = self._get_category(request.url.path)
        config = self.configs.get(category, self.configs["default"])

        current_time = time.time()
        request_times = self._requests.get(key, [])

        # 计算最近1分钟的请求数
        minute_requests = sum(1 for t in request_times if current_time - t < 60)
        # 计算最近1小时的请求数
        hour_requests = sum(1 for t in request_times if current_time - t < 3600)

        return {
            "limit_minute": config.requests_per_minute,
            "remaining_minute": max(0, config.requests_per_minute - minute_requests),
            "limit_hour": config.requests_per_hour,
            "remaining_hour": max(0, config.requests_per_hour - hour_requests),
        }


rate_limiter = RateLimiter()


# ============ 输入验证 ============

class SecurityValidator:
    """安全验证器"""

    # 常见的攻击模式
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bexec\b|\bexecute\b)",
        r"(;.*\b(exec|execute|select|insert|delete|update|drop)\b)",
        r"('''.*''')|(''.*'')",
        r"(--)",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e",
        r"\.\.%2f",
        r"%2e%2e%2f",
    ]

    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\([^)]*\)",
        r"`[^`]*`",
    ]

    @classmethod
    def check_sql_injection(cls, text: str) -> bool:
        """检查 SQL 注入"""
        text_lower = text.lower()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    @classmethod
    def check_xss(cls, text: str) -> bool:
        """检查 XSS 攻击"""
        text_lower = text.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    @classmethod
    def check_path_traversal(cls, text: str) -> bool:
        """检查路径遍历攻击"""
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def check_command_injection(cls, text: str) -> bool:
        """检查命令注入"""
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                return True
        return False

    @classmethod
    def validate_input(cls, value: Any, field_name: str = "input") -> None:
        """验证输入安全性"""
        if value is None:
            return

        if not isinstance(value, str):
            return

        # 检查各种攻击
        checks = [
            (cls.check_sql_injection, "SQL injection"),
            (cls.check_xss, "XSS"),
            (cls.check_path_traversal, "path traversal"),
            (cls.check_command_injection, "command injection"),
        ]

        for check_func, attack_type in checks:
            if check_func(value):
                logger.warning(f"Potential {attack_type} detected in {field_name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input: potential {attack_type} detected"
                )

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """简单的 HTML 清理"""
        # 移除危险的 HTML 标签
        dangerous_tags = ["<script", "</script", "<iframe", "</iframe",
                         "<embed", "</embed", "<object", "</object",
                         "javascript:", "onerror=", "onload="]

        result = text
        for tag in dangerous_tags:
            result = result.replace(tag, "")
        return result


validator = SecurityValidator()


# ============ 安全日志 ============

class SecurityLogger:
    """安全日志记录器"""

    def __init__(self, log_file: str = None):
        if log_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logs_dir = os.path.join(base_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            log_file = os.path.join(logs_dir, "security.log")

        self.log_file = log_file

        # 配置安全日志记录器
        self.logger = logging.getLogger("ai_coworker.security")
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        request: Request = None
    ):
        """记录安全事件"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details,
        }

        # 添加请求信息
        if request:
            log_data["request"] = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else None,
            }

        # 记录日志
        if severity == "high":
            self.logger.error(f"[{event_type}] {details}")
        elif severity == "medium":
            self.logger.warning(f"[{event_type}] {details}")
        else:
            self.logger.info(f"[{event_type}] {details}")

    def log_failed_auth(self, username: str, reason: str, request: Request):
        """记录认证失败"""
        self.log_security_event(
            event_type="AUTH_FAILURE",
            severity="high",
            details={
                "username": username,
                "reason": reason,
            },
            request=request
        )

    def log_rate_limit_exceeded(self, identifier: str, request: Request):
        """记录 Rate limit 超过"""
        self.log_security_event(
            event_type="RATE_LIMIT_EXCEEDED",
            severity="medium",
            details={"identifier": identifier},
            request=request
        )

    def log_invalid_input(self, field_name: str, value: str, reason: str, request: Request):
        """记录无效输入"""
        self.log_security_event(
            event_type="INVALID_INPUT",
            severity="medium",
            details={
                "field": field_name,
                "reason": reason,
                "value_length": len(value),
            },
            request=request
        )

    def log_csrf_failure(self, reason: str, request: Request):
        """记录 CSRF 验证失败"""
        self.log_security_event(
            event_type="CSRF_FAILURE",
            severity="high",
            details={"reason": reason},
            request=request
        )


security_logger = SecurityLogger()


# ============ 中间件 ============

class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""

    # CSRF 白名单路径
    CSRF_WHITELIST = {
        "/api/health",
        "/api/performance",
        "/api/features",
        "/login",
        "/api/auth/login",
        "/api/auth/register",
    }

    def __init__(self, app):
        super().__init__(app)
        # 定期清理过期的 CSRF token
        self._cleanup_interval = 600  # 10分钟
        self._last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 清理过期的 CSRF token
        self._cleanup_if_needed()

        # Rate limiting
        allowed, reason = rate_limiter.check_rate_limit(request)
        if not allowed:
            security_logger.log_rate_limit_exceeded(
                identifier=request.client.host if request.client else "unknown",
                request=request
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": reason}
            )

        # CSRF 保护（仅对状态改变请求）
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # 检查是否在白名单中
            if not self._is_csrf_whitelisted(request.url.path):
                csrf_token = request.headers.get("X-CSRF-Token")
                session_id = request.cookies.get("session_id", "")

                if not csrf_token or not csrf_manager.validate_token(csrf_token, session_id):
                    security_logger.log_csrf_failure(
                        reason="Invalid or missing CSRF token",
                        request=request
                    )
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Invalid CSRF token"}
                    )

        # 设置安全响应头
        response = await call_next(request)

        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 添加 rate limit 信息
        rate_info = rate_limiter.get_rate_limit_info(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(rate_info["limit_minute"])
        response.headers["X-RateLimit-Remaining-Minute"] = str(rate_info["remaining_minute"])
        response.headers["X-RateLimit-Limit-Hour"] = str(rate_info["limit_hour"])
        response.headers["X-RateLimit-Remaining-Hour"] = str(rate_info["remaining_hour"])

        # 暴露 CSRF token 头（用于前端获取新 token）
        response.headers["Access-Control-Expose-Headers"] = "X-CSRF-Token,X-RateLimit-*"

        return response

    def _is_csrf_whitelisted(self, path: str) -> bool:
        """检查路径是否在 CSRF 白名单中"""
        for whitelist_path in self.CSRF_WHITELIST:
            if path.startswith(whitelist_path):
                return True
        return False

    def _cleanup_if_needed(self):
        """如果需要，清理过期的数据"""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            csrf_manager.cleanup_expired_tokens()
            self._last_cleanup = current_time
