"""测试用户认证系统

测试用户注册、登录、JWT token验证等功能
"""

import pytest
import tempfile
import os
from core.auth import AuthManager, User, UserRole, hash_password


class TestAuthentication:
    """测试认证系统功能"""

    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def auth_manager(self, temp_db):
        """创建认证管理器实例"""
        return AuthManager(db_path=temp_db, secret_key="test_secret_key")

    def test_hash_password(self, auth_manager):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = hash_password(password)

        # 验证哈希值不一致（因为包含salt）
        assert hashed != password

        # 验证相同密码产生相同哈希
        assert hash_password(password) == hashed

        # 验证不同密码产生不同哈希
        assert hash_password("different_password") != hashed

    def test_create_user(self, auth_manager):
        """测试创建用户"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=UserRole.USER
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_duplicate_username(self, auth_manager):
        """测试创建重复用户名"""
        auth_manager.create_user(
            username="testuser",
            email="test1@example.com",
            password="password123"
        )

        with pytest.raises(ValueError, match="用户名已存在"):
            auth_manager.create_user(
                username="testuser",
                email="test2@example.com",
                password="password456"
            )

    def test_create_duplicate_email(self, auth_manager):
        """测试创建重复邮箱"""
        auth_manager.create_user(
            username="user1",
            email="test@example.com",
            password="password123"
        )

        with pytest.raises(ValueError, match="邮箱已被使用"):
            auth_manager.create_user(
                username="user2",
                email="test@example.com",
                password="password456"
            )

    def test_get_user_by_username(self, auth_manager):
        """测试通过用户名获取用户"""
        created_user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        found_user = auth_manager.get_user_by_username("testuser")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "testuser"
        assert found_user.email == "test@example.com"

    def test_get_user_by_email(self, auth_manager):
        """测试通过邮箱获取用户"""
        created_user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        found_user = auth_manager.get_user_by_email("test@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"

    def test_get_user_by_id(self, auth_manager):
        """测试通过ID获取用户"""
        created_user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        found_user = auth_manager.get_user_by_id(created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id

    def test_authenticate_success(self, auth_manager):
        """测试成功认证"""
        auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        user = auth_manager.authenticate("testuser", "password123")

        assert user is not None
        assert user.username == "testuser"
        assert user.last_login is not None

    def test_authenticate_wrong_password(self, auth_manager):
        """测试错误密码"""
        auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        user = auth_manager.authenticate("testuser", "wrong_password")

        assert user is None

    def test_authenticate_nonexistent_user(self, auth_manager):
        """测试不存在的用户"""
        user = auth_manager.authenticate("nonexistent", "password")

        assert user is None

    def test_authenticate_inactive_user(self, auth_manager):
        """测试禁用用户认证"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        # 禁用用户
        auth_manager.toggle_user_active(user.id)

        with pytest.raises(ValueError, match="用户账户已被禁用"):
            auth_manager.authenticate("testuser", "password123")

    def test_create_access_token(self, auth_manager):
        """测试创建JWT token"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        token = auth_manager.create_access_token(user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_success(self, auth_manager):
        """测试验证有效token"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        token = auth_manager.create_access_token(user)
        payload = auth_manager.verify_token(token)

        assert payload is not None
        assert payload["sub"] == user.id
        assert payload["username"] == user.username
        assert payload["role"] == user.role.value
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_invalid(self, auth_manager):
        """测试验证无效token"""
        payload = auth_manager.verify_token("invalid_token")

        assert payload is None

    def test_list_users(self, auth_manager):
        """测试列出所有用户"""
        auth_manager.create_user("user1", "user1@example.com", "pass1")
        auth_manager.create_user("user2", "user2@example.com", "pass2")
        auth_manager.create_user("user3", "user3@example.com", "pass3")

        users = auth_manager.list_users()

        assert len(users) == 3
        usernames = [u.username for u in users]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames

    def test_update_user_role(self, auth_manager):
        """测试更新用户角色"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=UserRole.USER
        )

        success = auth_manager.update_user_role(user.id, UserRole.ADMIN)

        assert success is True

        updated_user = auth_manager.get_user_by_id(user.id)
        assert updated_user.role == UserRole.ADMIN

    def test_toggle_user_active(self, auth_manager):
        """测试切换用户激活状态"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        # 禁用用户
        success = auth_manager.toggle_user_active(user.id)
        assert success is True

        inactive_user = auth_manager.get_user_by_id(user.id)
        assert inactive_user.is_active is False

        # 重新激活用户
        success = auth_manager.toggle_user_active(user.id)
        assert success is True

        active_user = auth_manager.get_user_by_id(user.id)
        assert active_user.is_active is True

    def test_user_to_dict(self, auth_manager):
        """测试用户转换为字典"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role=UserRole.ADMIN
        )

        user_dict = user.to_dict()

        assert user_dict["id"] == user.id
        assert user_dict["username"] == user.username
        assert user_dict["email"] == user.email
        assert user_dict["role"] == "admin"
        assert user_dict["is_active"] is True
        assert "created_at" in user_dict
        assert "hashed_password" not in user_dict  # 敏感信息不应包含

    def test_user_to_dict_with_sensitive(self, auth_manager):
        """测试用户转换包含敏感信息"""
        user = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        user_dict = user.to_dict(include_sensitive=True)

        assert "hashed_password" in user_dict
