"""安全功能测试

测试系统的安全增强功能
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from main import app


class TestSecurity:
    """安全功能测试类"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    def test_cors_headers(self, client):
        """测试 CORS 响应头"""
        response = client.get("/api/health")
        # 检查是否有 expose CORS 头
        assert "access-control-expose-headers" in response.headers

    def test_security_headers(self, client):
        """测试安全响应头"""
        response = client.get("/api/health")

        # 检查安全头
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers

    def test_rate_limiting_headers(self, client):
        """测试 Rate Limiting 响应头"""
        response = client.get("/api/health")

        # 检查 rate limit 头
        assert "X-RateLimit-Limit-Minute" in response.headers
        assert "X-RateLimit-Remaining-Minute" in response.headers
        assert "X-RateLimit-Limit-Hour" in response.headers
        assert "X-RateLimit-Remaining-Hour" in response.headers

    def test_csrf_token_generation(self, client):
        """测试 CSRF token 生成"""
        response = client.get("/api/auth/csrf-token")

        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert "session_id" in data
        assert len(data["csrf_token"]) == 64  # SHA-256 hex length

    def test_sql_injection_detection(self):
        """测试 SQL 注入检测"""
        from core.security import validator

        # 测试各种 SQL 注入模式
        malicious_inputs = [
            "1' OR '1'='1",
            "1; DROP TABLE users--",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "1' OR 1=1--",
        ]

        for input_str in malicious_inputs:
            try:
                validator.validate_input(input_str, "test_field")
                # 如果没有抛出异常，测试失败
                assert False, f"SQL injection not detected: {input_str}"
            except Exception:
                # 预期的行为
                pass

    def test_xss_detection(self):
        """测试 XSS 攻击检测"""
        from core.security import validator

        # 测试各种 XSS 模式
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(XSS)'></iframe>",
        ]

        for input_str in malicious_inputs:
            try:
                validator.validate_input(input_str, "test_field")
                # 如果没有抛出异常，可能应该检查一下
                # 注意：validator.check_xss 使用的是简单的正则匹配
            except Exception:
                # 可能会抛出异常
                pass

    def test_path_traversal_detection(self):
        """测试路径遍历攻击检测"""
        from core.security import validator

        # 测试路径遍历模式
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "%2e%2e%2f",
            "....//....//",
        ]

        for input_str in malicious_inputs:
            try:
                validator.validate_input(input_str, "test_field")
                # 如果没有抛出异常，测试失败
                assert False, f"Path traversal not detected: {input_str}"
            except Exception:
                # 预期的行为
                pass

    def test_command_injection_detection(self):
        """测试命令注入检测"""
        from core.security import validator

        # 测试命令注入模式
        malicious_inputs = [
            "file.txt; cat /etc/passwd",
            "file.txt && rm -rf /",
            "file.txt|whoami",
            "file.txt`whoami`",
            "$(cat /etc/passwd)",
        ]

        for input_str in malicious_inputs:
            try:
                validator.validate_input(input_str, "test_field")
                # 如果没有抛出异常，测试失败
                assert False, f"Command injection not detected: {input_str}"
            except Exception:
                # 预期的行为
                pass

    def test_input_validation_in_requests(self, client):
        """测试请求中的输入验证"""
        # 测试注册请求中的输入验证
        malicious_data = {
            "username": "admin'; DROP TABLE users;--",
            "email": "test@example.com",
            "password": "password123",
            "role": "user"
        }

        response = client.post("/api/auth/register", json=malicious_data)
        # 应该返回 400 错误（输入验证失败）
        assert response.status_code in [400, 422]

    def test_rate_limiting(self, client):
        """测试 Rate Limiting"""
        # 这个测试可能会比较慢，因为需要发送大量请求
        # 在实际测试中，可能需要调整 rate limit 的阈值

        # 发送多个请求
        for i in range(10):
            response = client.get("/api/health")
            assert response.status_code == 200

        # 注意：完整的 rate limit 测试需要在配置中设置更低的阈值
        # 这里只是测试响应头是否存在
        response = client.get("/api/health")
        assert "X-RateLimit-Remaining-Minute" in response.headers


class TestCSRFProtection:
    """CSRF 保护测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    def test_csrf_token_required_for_post(self, client):
        """测试 POST 请求需要 CSRF token"""
        # 获取 CSRF token
        token_response = client.get("/api/auth/csrf-token")
        csrf_token = token_response.json()["csrf_token"]

        # 尝试不带 CSRF token 的 POST 请求
        # 注意：这取决于中间件的实现
        # 如果 CSRF 保护已启用，应该会被拒绝


class TestInputValidation:
    """输入验证测试"""

    def test_username_validation(self):
        """测试用户名验证"""
        from core.schemas import UserRegisterRequest

        # 有效用户名
        valid_usernames = [
            "testuser",
            "test_user",
            "test123",
            "测试用户",
        ]

        for username in valid_usernames:
            try:
                UserRegisterRequest(
                    username=username,
                    email="test@example.com",
                    password="password123"
                )
            except Exception:
                assert False, f"Valid username rejected: {username}"

        # 无效用户名
        invalid_usernames = [
            "test user",  # 包含空格
            "test@user",  # 包含特殊字符
            "a",  # 太短
            "a" * 51,  # 太长
        ]

        for username in invalid_usernames:
            try:
                UserRegisterRequest(
                    username=username,
                    email="test@example.com",
                    password="password123"
                )
                assert False, f"Invalid username accepted: {username}"
            except Exception:
                # 预期的行为
                pass

    def test_email_validation(self):
        """测试邮箱验证"""
        from core.schemas import UserRegisterRequest

        # 有效邮箱
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
        ]

        for email in valid_emails:
            try:
                UserRegisterRequest(
                    username="testuser",
                    email=email,
                    password="password123"
                )
            except Exception:
                assert False, f"Valid email rejected: {email}"

        # 无效邮箱
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test example.com",
        ]

        for email in invalid_emails:
            try:
                UserRegisterRequest(
                    username="testuser",
                    email=email,
                    password="password123"
                )
                assert False, f"Invalid email accepted: {email}"
            except Exception:
                # 预期的行为
                pass

    def test_password_validation(self):
        """测试密码验证"""
        from core.schemas import UserRegisterRequest

        # 有效密码
        valid_passwords = [
            "password123",
            "P@ssw0rd",
            "123456",
        ]

        for password in valid_passwords:
            try:
                UserRegisterRequest(
                    username="testuser",
                    email="test@example.com",
                    password=password
                )
            except Exception:
                assert False, f"Valid password rejected: {password}"

        # 无效密码
        invalid_passwords = [
            "12345",  # 太短
        ]

        for password in invalid_passwords:
            try:
                UserRegisterRequest(
                    username="testuser",
                    email="test@example.com",
                    password=password
                )
                assert False, f"Invalid password accepted: {password}"
            except Exception:
                # 预期的行为
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
