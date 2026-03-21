"""Tests for core.orchestrator module"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from core.orchestrator import (
    AgentState,
    MultiAgentOrchestrator
)
from core.storage import Session, Task, TaskState, AgentRole, Message, MessageType
from core.agents import AgentRole as AgentRoleEnum


class TestAgentState:
    """Test AgentState TypedDict"""

    def test_agent_state_creation(self):
        """Test creating an AgentState"""
        session = Session()
        state = AgentState(
            session=session,
            messages=[],
            current_agent=None,
            pending_approval=None,
            task_updates=[]
        )
        assert state["session"] == session
        assert state["messages"] == []
        assert state["current_agent"] is None
        assert state["pending_approval"] is None
        assert state["task_updates"] == []

    def test_agent_state_with_values(self):
        """Test AgentState with populated values"""
        session = Session(id="test_session")
        msg = Message(
            id="msg1",
            sender="user",
            sender_role="user",
            content="Hello",
            message_type=MessageType.USER
        )

        state = AgentState(
            session=session,
            messages=[msg],
            current_agent="dev",
            pending_approval={"type": "task_create"},
            task_updates=["task1"]
        )

        assert state["session"].id == "test_session"
        assert len(state["messages"]) == 1
        assert state["current_agent"] == "dev"
        assert state["pending_approval"]["type"] == "task_create"
        assert state["task_updates"] == ["task1"]


class TestMultiAgentOrchestrator:
    """Test MultiAgentOrchestrator class"""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM"""
        llm = Mock()
        llm.invoke = Mock()
        return llm

    @pytest.fixture
    def orchestrator(self, mock_llm):
        """Create an orchestrator instance with mock LLM"""
        return MultiAgentOrchestrator(llm=mock_llm)

    def test_orchestrator_initialization_with_llm(self, mock_llm):
        """Test orchestrator initialization with provided LLM"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        assert orch.llm == mock_llm
        assert orch.model == "gpt-4"
        assert orch.api_key is None
        assert orch.base_url is None

    def test_orchestrator_initialization_with_params(self):
        """Test orchestrator initialization with model parameters"""
        orch = MultiAgentOrchestrator(
            model="gpt-4o",
            api_key="test-key",
            base_url="https://api.test.com"
        )
        assert orch.model == "gpt-4o"
        assert orch.api_key == "test-key"
        assert orch.base_url == "https://api.test.com"
        assert orch.llm is not None

    def test_orchestrator_initialization_default(self):
        """Test orchestrator initialization with defaults"""
        orch = MultiAgentOrchestrator()
        assert orch.model == "gpt-4"
        assert orch.llm is not None

    def test_orchestrator_has_feature_list(self, orchestrator):
        """Test that orchestrator has feature list initialized"""
        assert orchestrator.feature_list is not None

    def test_orchestrator_has_graph(self, orchestrator):
        """Test that orchestrator builds graph"""
        assert orchestrator.graph is not None

    @patch('core.orchestrator.ChatOpenAI')
    def test_orchestrator_creates_openai_llm(self, mock_chat_openai):
        """Test that orchestrator creates OpenAI LLM when no LLM provided"""
        mock_llm_instance = Mock()
        mock_chat_openai.return_value = mock_llm_instance

        orch = MultiAgentOrchestrator(
            model="gpt-4o",
            api_key="test-key"
        )

        assert orch.llm == mock_llm_instance
        mock_chat_openai.assert_called_once()

    @patch('core.orchestrator.ChatOpenAI')
    def test_orchestrator_creates_openai_llm_with_base_url(self, mock_chat_openai):
        """Test that orchestrator creates OpenAI LLM with custom base URL"""
        mock_llm_instance = Mock()
        mock_chat_openai.return_value = mock_llm_instance

        orch = MultiAgentOrchestrator(
            model="gpt-4o",
            api_key="test-key",
            base_url="https://custom.api.com/v1"
        )

        assert orch.llm == mock_llm_instance

    def test_orchestrator_with_project_dir(self):
        """Test orchestrator initialization with project directory"""
        orch = MultiAgentOrchestrator(project_dir="test_project")
        assert orch.feature_list is not None


class TestOrchestratorIntegration:
    """Integration tests for orchestrator workflows"""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM with predefined responses"""
        llm = Mock()
        # Create mock response
        mock_response = Mock()
        mock_response.content = "Test response from agent"
        llm.invoke.return_value = mock_response
        return llm

    def test_create_session(self, mock_llm):
        """Test creating a new session through orchestrator"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()
        assert session is not None
        assert session.id is not None

    def test_session_state_management(self, mock_llm):
        """Test managing session state in orchestrator"""
        orch = MultiAgentOrchestrator(llm=mock_llm)

        # Create initial state
        session = Session()
        state = AgentState(
            session=session,
            messages=[],
            current_agent=None,
            pending_approval=None,
            task_updates=[]
        )

        assert state["session"].is_active is True
        assert state["session"].turn_count == 0

    def test_state_with_task_updates(self, mock_llm):
        """Test state tracking task updates"""
        orch = MultiAgentOrchestrator(llm=mock_llm)

        session = Session()
        task = Task(
            id="task1",
            title="Test Task",
            description="A test task",
            state=TaskState.IN_PROGRESS
        )
        session.tasks["task1"] = task

        state = AgentState(
            session=session,
            messages=[],
            current_agent="dev",
            pending_approval=None,
            task_updates=["task1"]
        )

        assert "task1" in state["task_updates"]
        assert state["session"].tasks["task1"].state == TaskState.IN_PROGRESS


class TestOrchestratorStateTransitions:
    """Test orchestrator state transitions and agent routing"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for state transition tests"""
        llm = Mock()
        mock_response = Mock()
        mock_response.content = "I will work on this task."
        llm.invoke.return_value = mock_response
        return llm

    def test_initial_state(self, mock_llm):
        """Test initial orchestrator state"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        state = AgentState(
            session=session,
            messages=[],
            current_agent=None,
            pending_approval=None,
            task_updates=[]
        )

        assert state["current_agent"] is None
        assert len(state["messages"]) == 0

    def test_state_with_active_agent(self, mock_llm):
        """Test state with current agent set"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        state = AgentState(
            session=session,
            messages=[],
            current_agent="dev",
            pending_approval=None,
            task_updates=[]
        )

        assert state["current_agent"] == "dev"

    def test_state_with_pending_approval(self, mock_llm):
        """Test state with pending approval"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        approval_data = {
            "type": "hire_agent",
            "role": "dev",
            "reason": "Need more developers"
        }

        state = AgentState(
            session=session,
            messages=[],
            current_agent="hr",
            pending_approval=approval_data,
            task_updates=[]
        )

        assert state["pending_approval"]["type"] == "hire_agent"
        assert state["current_agent"] == "hr"


class TestOrchestratorMessageHandling:
    """Test orchestrator message handling"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for message handling tests"""
        llm = Mock()
        mock_response = Mock()
        mock_response.content = "Message processed"
        llm.invoke.return_value = mock_response
        return llm

    def test_state_with_messages(self, mock_llm):
        """Test state with message history"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        msg1 = Message(
            id="msg1",
            sender="user",
            sender_role="user",
            content="User message",
            message_type=MessageType.USER
        )

        msg2 = Message(
            id="msg2",
            sender="dev_agent",
            sender_role="dev",
            content="Agent response",
            message_type=MessageType.AGENT
        )

        state = AgentState(
            session=session,
            messages=[msg1, msg2],
            current_agent=None,
            pending_approval=None,
            task_updates=[]
        )

        assert len(state["messages"]) == 2
        assert state["messages"][0].sender == "user"
        assert state["messages"][1].sender == "dev_agent"

    def test_message_accumulation(self, mock_llm):
        """Test that messages accumulate correctly"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        # Add messages to session (not just state)
        for i in range(5):
            msg = Message(
                id=f"msg{i}",
                sender="user" if i % 2 == 0 else "agent",
                sender_role="user" if i % 2 == 0 else "dev",
                content=f"Message {i}",
                message_type=MessageType.USER if i % 2 == 0 else MessageType.AGENT
            )
            session.add_message(msg)

        state = AgentState(
            session=session,
            messages=session.messages,
            current_agent=None,
            pending_approval=None,
            task_updates=[]
        )

        assert len(state["messages"]) == 5
        assert session.turn_count == 5  # User and agent messages both count


class TestOrchestratorWithTasks:
    """Test orchestrator with task management"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for task tests"""
        llm = Mock()
        mock_response = Mock()
        mock_response.content = "Task updated"
        llm.invoke.return_value = mock_response
        return llm

    def test_state_with_tasks_in_session(self, mock_llm):
        """Test state with tasks in session"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        task1 = Task(
            id="task1",
            title="Task 1",
            description="First task",
            state=TaskState.DONE
        )

        task2 = Task(
            id="task2",
            title="Task 2",
            description="Second task",
            state=TaskState.IN_PROGRESS
        )

        session.tasks["task1"] = task1
        session.tasks["task2"] = task2

        state = AgentState(
            session=session,
            messages=[],
            current_agent="dev",
            pending_approval=None,
            task_updates=["task2"]
        )

        assert len(state["session"].tasks) == 2
        assert state["session"].tasks["task1"].state == TaskState.DONE
        assert state["session"].tasks["task2"].state == TaskState.IN_PROGRESS
        assert "task2" in state["task_updates"]

    def test_task_updates_tracking(self, mock_llm):
        """Test tracking task updates in state"""
        orch = MultiAgentOrchestrator(llm=mock_llm)
        session = Session()

        state = AgentState(
            session=session,
            messages=[],
            current_agent="pm",
            pending_approval=None,
            task_updates=["task1", "task2", "task3"]
        )

        assert len(state["task_updates"]) == 3
        assert "task1" in state["task_updates"]
        assert "task2" in state["task_updates"]
        assert "task3" in state["task_updates"]
