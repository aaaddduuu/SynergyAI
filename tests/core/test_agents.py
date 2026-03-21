"""Tests for core.agents module"""

import pytest
from core.agents import (
    AgentRole,
    get_agent_prompt,
    get_agent_description,
    TaskOperation
)


class TestAgentRole:
    """Test AgentRole enum"""

    def test_agent_role_values(self):
        """Test that all agent roles have correct values"""
        assert AgentRole.HR.value == "hr"
        assert AgentRole.PM.value == "pm"
        assert AgentRole.BA.value == "ba"
        assert AgentRole.DEV.value == "dev"
        assert AgentRole.QA.value == "qa"
        assert AgentRole.ARCHITECT.value == "architect"
        assert AgentRole.ORCHESTRATOR.value == "orchestrator"

    def test_agent_role_iteration(self):
        """Test that we can iterate over all agent roles"""
        roles = list(AgentRole)
        assert len(roles) == 7
        assert AgentRole.HR in roles
        assert AgentRole.DEV in roles


class TestAgentPrompts:
    """Test agent prompt generation functions"""

    def test_get_agent_prompt_without_name(self):
        """Test getting agent prompt without providing name"""
        prompt = get_agent_prompt(AgentRole.DEV)
        assert prompt is not None
        assert len(prompt) > 0
        assert "开发工程师" in prompt

    def test_get_agent_prompt_with_name(self):
        """Test getting agent prompt with custom name"""
        prompt = get_agent_prompt(AgentRole.QA, "测试工程师小李")
        assert "你的名字是 测试工程师小李" in prompt
        assert "测试工程师" in prompt

    def test_get_agent_prompt_all_roles(self):
        """Test that all agent roles have prompts (excluding orchestrator)"""
        for role in AgentRole:
            if role == AgentRole.ORCHESTRATOR:
                continue  # Orchestrator role doesn't have a system prompt
            prompt = get_agent_prompt(role)
            assert prompt is not None
            assert len(prompt) > 0

    def test_get_agent_description(self):
        """Test getting agent descriptions"""
        desc = get_agent_description(AgentRole.HR)
        assert "HR" in desc
        assert "团队协调" in desc

        desc = get_agent_description(AgentRole.PM)
        assert "项目经理" in desc
        assert "进度管理" in desc

        desc = get_agent_description(AgentRole.DEV)
        assert "开发工程师" in desc
        assert "功能开发" in desc


class TestTaskOperation:
    """Test TaskOperation parsing"""

    def test_parse_create_operation(self):
        """Test parsing create task operation"""
        text = "[任务] 创建: 用户登录功能 | 实现用户登录 | dev | high"
        operations = TaskOperation.parse(text)

        assert len(operations) == 1
        assert operations[0]['action'] == 'create'
        assert operations[0]['title'] == '用户登录功能'
        assert operations[0]['description'] == '实现用户登录'
        assert operations[0]['assignee_role'] == 'dev'
        assert operations[0]['priority'] == 'high'

    def test_parse_state_operation(self):
        """Test parsing state update operation"""
        text = "[任务] 状态: 用户登录功能 | done"
        operations = TaskOperation.parse(text)

        assert len(operations) == 1
        assert operations[0]['action'] == 'update_state'
        assert operations[0]['title'] == '用户登录功能'
        assert operations[0]['state'] == 'done'

    def test_parse_assign_operation(self):
        """Test parsing assign operation"""
        text = "[任务] 分配: 用户登录功能 | qa"
        operations = TaskOperation.parse(text)

        assert len(operations) == 1
        assert operations[0]['action'] == 'assign'
        assert operations[0]['title'] == '用户登录功能'
        assert operations[0]['assignee_role'] == 'qa'

    def test_parse_delete_operation(self):
        """Test parsing delete operation"""
        text = "[任务] 删除: 测试任务"
        operations = TaskOperation.parse(text)

        assert len(operations) == 1
        assert operations[0]['action'] == 'delete'
        assert operations[0]['title'] == '测试任务'

    def test_parse_multiple_operations(self):
        """Test parsing multiple operations in one text"""
        text = """
        [任务] 创建: 功能A | 描述A | dev | high
        [任务] 状态: 功能B | done
        [任务] 分配: 功能C | qa
        """
        operations = TaskOperation.parse(text)

        assert len(operations) == 3
        assert operations[0]['action'] == 'create'
        assert operations[1]['action'] == 'update_state'
        assert operations[2]['action'] == 'assign'

    def test_parse_operation_with_extra_spaces(self):
        """Test parsing operations with irregular spacing"""
        text = "[任务] 创建:  标题  |  描述  |  dev  |  high  "
        operations = TaskOperation.parse(text)

        assert len(operations) == 1
        assert operations[0]['title'] == '标题'
        assert operations[0]['description'] == '描述'

    def test_has_operation_true(self):
        """Test has_operation returns True when operation exists"""
        assert TaskOperation.has_operation("[任务] 创建: 标题 | 描述 | dev | high")
        assert TaskOperation.has_operation("[任务] 状态: 标题 | done")
        assert TaskOperation.has_operation("[任务] 分配: 标题 | qa")
        assert TaskOperation.has_operation("[任务] 删除: 标题")

    def test_has_operation_false(self):
        """Test has_operation returns False when no operation exists"""
        assert not TaskOperation.has_operation("这是普通文本")
        assert not TaskOperation.has_operation("没有任务操作的文本")
        assert not TaskOperation.has_operation("")

    def test_parse_case_insensitive(self):
        """Test that parsing accepts uppercase but preserves it"""
        text = "[任务] 创建: 标题 | 描述 | DEV | HIGH"
        operations = TaskOperation.parse(text)

        assert len(operations) == 1
        # Regex matches case-insensitively but preserves original case
        assert operations[0]['assignee_role'] == 'DEV'
        assert operations[0]['priority'] == 'HIGH'

    def test_parse_empty_text(self):
        """Test parsing empty text"""
        operations = TaskOperation.parse("")
        assert len(operations) == 0

    def test_parse_text_without_operations(self):
        """Test parsing text without task operations"""
        text = "这是一段普通的对话文本，不包含任何任务操作。"
        operations = TaskOperation.parse(text)
        assert len(operations) == 0

    def test_parse_invalid_operation_format(self):
        """Test parsing operations with invalid format"""
        # Missing required fields
        text = "[任务] 创建: 标题"
        operations = TaskOperation.parse(text)
        assert len(operations) == 0

    def test_all_valid_states(self):
        """Test parsing all valid task states"""
        states = ['pending', 'in_progress', 'review', 'done']
        for state in states:
            text = f"[任务] 状态: 任务 | {state}"
            operations = TaskOperation.parse(text)
            assert len(operations) == 1
            assert operations[0]['state'] == state

    def test_all_valid_roles(self):
        """Test parsing all valid assignee roles"""
        roles = ['dev', 'qa', 'ba', 'architect', 'pm']
        for role in roles:
            text = f"[任务] 创建: 任务 | 描述 | {role} | high"
            operations = TaskOperation.parse(text)
            assert len(operations) == 1
            assert operations[0]['assignee_role'] == role

    def test_all_valid_priorities(self):
        """Test parsing all valid priorities"""
        priorities = ['low', 'medium', 'high']
        for priority in priorities:
            text = f"[任务] 创建: 任务 | 描述 | dev | {priority}"
            operations = TaskOperation.parse(text)
            assert len(operations) == 1
            assert operations[0]['priority'] == priority
