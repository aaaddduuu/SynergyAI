"""Tests for core.storage module"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from core.storage import (
    TaskState,
    AgentRole,
    MessageType,
    Message,
    Task,
    Agent,
    Session,
    Storage
)


class TestTaskState:
    """Test TaskState enum"""

    def test_task_state_values(self):
        """Test that all task states have correct values"""
        assert TaskState.PENDING.value == "pending"
        assert TaskState.IN_PROGRESS.value == "in_progress"
        assert TaskState.REVIEW.value == "review"
        assert TaskState.DONE.value == "done"
        assert TaskState.BLOCKED.value == "blocked"

    def test_task_state_iteration(self):
        """Test that we can iterate over all task states"""
        states = list(TaskState)
        assert len(states) == 5
        assert TaskState.PENDING in states
        assert TaskState.DONE in states


class TestMessageType:
    """Test MessageType enum"""

    def test_message_type_values(self):
        """Test that all message types have correct values"""
        assert MessageType.USER.value == "user"
        assert MessageType.AGENT.value == "agent"
        assert MessageType.SYSTEM.value == "system"
        assert MessageType.TASK_UPDATE.value == "task_update"
        assert MessageType.REQUEST.value == "request"


class TestMessage:
    """Test Message dataclass"""

    def test_message_creation(self):
        """Test creating a message"""
        msg = Message(
            id="msg1",
            sender="user",
            sender_role="user",
            content="Hello",
            message_type=MessageType.USER
        )
        assert msg.id == "msg1"
        assert msg.sender == "user"
        assert msg.content == "Hello"
        assert msg.message_type == MessageType.USER
        assert isinstance(msg.timestamp, datetime)
        assert msg.metadata == {}

    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        msg = Message(
            id="msg1",
            sender="dev_agent",
            sender_role="dev",
            content="Task completed",
            message_type=MessageType.AGENT,
            metadata={"task_id": "task1"}
        )
        msg_dict = msg.to_dict()

        assert msg_dict["id"] == "msg1"
        assert msg_dict["sender"] == "dev_agent"
        assert msg_dict["sender_role"] == "dev"
        assert msg_dict["content"] == "Task completed"
        assert msg_dict["message_type"] == "agent"
        assert "timestamp" in msg_dict
        assert msg_dict["metadata"]["task_id"] == "task1"

    def test_message_with_metadata(self):
        """Test message with custom metadata"""
        msg = Message(
            id="msg2",
            sender="system",
            sender_role="system",
            content="System notification",
            message_type=MessageType.SYSTEM,
            metadata={"priority": "high", "category": "alert"}
        )
        assert msg.metadata["priority"] == "high"
        assert msg.metadata["category"] == "alert"


class TestTask:
    """Test Task dataclass"""

    def test_task_creation_defaults(self):
        """Test creating a task with default values"""
        task = Task(
            id="task1",
            title="Test Task",
            description="A test task"
        )
        assert task.id == "task1"
        assert task.title == "Test Task"
        assert task.description == "A test task"
        assert task.assignee is None
        assert task.assignee_role is None
        assert task.state == TaskState.PENDING
        assert task.created_by == ""
        assert task.priority == "medium"
        assert task.dependencies == []
        assert task.notes == []
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_creation_full(self):
        """Test creating a task with all fields"""
        task = Task(
            id="task2",
            title="Full Task",
            description="Task with all fields",
            assignee="dev_agent",
            assignee_role=AgentRole.DEV,
            state=TaskState.IN_PROGRESS,
            created_by="pm",
            priority="high",
            dependencies=["task1"],
            notes=["Note 1", "Note 2"]
        )
        assert task.assignee == "dev_agent"
        assert task.assignee_role == AgentRole.DEV
        assert task.state == TaskState.IN_PROGRESS
        assert task.created_by == "pm"
        assert task.priority == "high"
        assert len(task.dependencies) == 1
        assert len(task.notes) == 2

    def test_task_to_dict(self):
        """Test converting task to dictionary"""
        task = Task(
            id="task3",
            title="Dict Test",
            description="Test dict conversion",
            assignee="qa_agent",
            assignee_role=AgentRole.QA,
            state=TaskState.REVIEW,
            priority="high"
        )
        task_dict = task.to_dict()

        assert task_dict["id"] == "task3"
        assert task_dict["title"] == "Dict Test"
        assert task_dict["assignee"] == "qa_agent"
        assert task_dict["assignee_role"] == "qa"
        assert task_dict["state"] == "review"
        assert task_dict["priority"] == "high"
        assert "created_at" in task_dict
        assert "updated_at" in task_dict

    def test_task_to_dict_no_assignee_role(self):
        """Test converting task without assignee role to dict"""
        task = Task(
            id="task4",
            title="No Role",
            description="Task without assignee role"
        )
        task_dict = task.to_dict()
        assert task_dict["assignee_role"] is None


class TestAgent:
    """Test Agent dataclass"""

    def test_agent_creation_defaults(self):
        """Test creating an agent with default values"""
        agent = Agent(
            id="agent1",
            name="Dev Agent",
            role=AgentRole.DEV,
            description="Developer agent",
            system_prompt="You are a developer"
        )
        assert agent.id == "agent1"
        assert agent.name == "Dev Agent"
        assert agent.role == AgentRole.DEV
        assert agent.is_active is True
        assert agent.current_task_id is None
        assert agent.message_count == 0

    def test_agent_creation_full(self):
        """Test creating an agent with all fields"""
        agent = Agent(
            id="agent2",
            name="QA Agent",
            role=AgentRole.QA,
            description="QA agent",
            system_prompt="You are a QA engineer",
            is_active=False,
            current_task_id="task1",
            message_count=10
        )
        assert agent.is_active is False
        assert agent.current_task_id == "task1"
        assert agent.message_count == 10

    def test_agent_to_dict(self):
        """Test converting agent to dictionary"""
        agent = Agent(
            id="agent3",
            name="PM Agent",
            role=AgentRole.PM,
            description="Project manager",
            system_prompt="You are a PM"
        )
        agent_dict = agent.to_dict()

        assert agent_dict["id"] == "agent3"
        assert agent_dict["name"] == "PM Agent"
        assert agent_dict["role"] == "pm"
        assert agent_dict["description"] == "Project manager"
        assert agent_dict["is_active"] is True


class TestSession:
    """Test Session class"""

    def test_session_creation_with_id(self):
        """Test creating a session with specific ID"""
        session = Session(id="session1")
        assert session.id == "session1"
        assert session.messages == []
        assert session.agents == {}
        assert session.tasks == {}
        assert session.turn_count == 0
        assert session.is_active is True
        assert session.handover_doc is None
        assert isinstance(session.created_at, datetime)

    def test_session_creation_without_id(self):
        """Test creating a session without ID (auto-generate)"""
        session = Session()
        assert session.id is not None
        assert len(session.id) > 0
        assert isinstance(session.id, str)

    def test_add_message_user(self):
        """Test adding a user message increments turn count"""
        session = Session()
        msg = Message(
            id="msg1",
            sender="user",
            sender_role="user",
            content="Hello",
            message_type=MessageType.USER
        )
        session.add_message(msg)
        assert len(session.messages) == 1
        assert session.turn_count == 1

    def test_add_message_agent(self):
        """Test adding an agent message increments turn count"""
        session = Session()
        msg = Message(
            id="msg1",
            sender="agent",
            sender_role="dev",
            content="Response",
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        assert len(session.messages) == 1
        assert session.turn_count == 1

    def test_add_message_system(self):
        """Test adding a system message doesn't increment turn count"""
        session = Session()
        msg = Message(
            id="msg1",
            sender="system",
            sender_role="system",
            content="System message",
            message_type=MessageType.SYSTEM
        )
        session.add_message(msg)
        assert len(session.messages) == 1
        assert session.turn_count == 0

    def test_check_session_end_by_turns(self):
        """Test session ends after 30 turns"""
        session = Session()
        session.turn_count = 30
        should_end, reason = session.check_session_end()
        assert should_end is True
        assert reason == "conversation_30_turns"

    def test_check_session_end_by_task(self):
        """Test session ends when task is completed"""
        session = Session()
        task = Task(
            id="task1",
            title="Test Task",
            description="Test",
            state=TaskState.DONE
        )
        session.tasks["task1"] = task
        should_end, reason = session.check_session_end()
        assert should_end is True
        assert reason == "task_completed"

    def test_check_session_not_end(self):
        """Test session should not end"""
        session = Session()
        session.turn_count = 10
        task = Task(
            id="task1",
            title="Test Task",
            description="Test",
            state=TaskState.IN_PROGRESS
        )
        session.tasks["task1"] = task
        should_end, reason = session.check_session_end()
        assert should_end is False
        assert reason == ""

    def test_generate_handover_doc(self):
        """Test generating handover document"""
        session = Session(id="session1")
        task1 = Task(
            id="task1",
            title="Incomplete Task 1",
            description="Not done",
            state=TaskState.IN_PROGRESS,
            assignee="dev",
            priority="high",
            notes=["Need to review"]
        )
        task2 = Task(
            id="task2",
            title="Incomplete Task 2",
            description="Also not done",
            state=TaskState.PENDING,
            priority="medium"
        )
        session.tasks["task1"] = task1
        session.tasks["task2"] = task2

        doc = session.generate_handover_doc()
        assert "离职交接文档" in doc
        assert "session1" in doc
        assert "未完成任务 (2 项)" in doc
        assert "Incomplete Task 1" in doc
        assert "Incomplete Task 2" in doc

    def test_generate_handover_doc_all_complete(self):
        """Test handover doc when all tasks complete"""
        session = Session()
        task = Task(
            id="task1",
            title="Complete Task",
            description="Done",
            state=TaskState.DONE
        )
        session.tasks["task1"] = task

        doc = session.generate_handover_doc()
        assert "未完成任务 (0 项)" in doc


class TestStorage:
    """Test Storage class"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            yield db_path

    def test_storage_initialization(self, temp_db):
        """Test storage initializes and creates DB"""
        storage = Storage(db_path=temp_db)
        assert storage.db_path == temp_db
        assert os.path.exists(temp_db)

    def test_save_and_load_session(self, temp_db):
        """Test saving and loading a session"""
        storage = Storage(db_path=temp_db)

        # Create and save session
        session = Session(id="session1")
        msg = Message(
            id="msg1",
            sender="user",
            sender_role="user",
            content="Test",
            message_type=MessageType.USER
        )
        session.add_message(msg)

        task = Task(
            id="task1",
            title="Test Task",
            description="Test"
        )
        session.tasks["task1"] = task

        storage.save_session(session)

        # Load session
        loaded = storage.load_session("session1")
        assert loaded is not None
        assert loaded.id == "session1"
        assert len(loaded.messages) == 1
        assert len(loaded.tasks) == 1
        assert loaded.messages[0].content == "Test"
        assert loaded.tasks["task1"].title == "Test Task"

    def test_load_nonexistent_session(self, temp_db):
        """Test loading a session that doesn't exist"""
        storage = Storage(db_path=temp_db)
        loaded = storage.load_session("nonexistent")
        assert loaded is None

    def test_list_sessions(self, temp_db):
        """Test listing all sessions"""
        storage = Storage(db_path=temp_db)

        # Create multiple sessions
        for i in range(3):
            session = Session(id=f"session{i}")
            storage.save_session(session)

        # List sessions
        sessions = storage.list_sessions()
        assert len(sessions) == 3
        session_ids = [s["id"] for s in sessions]
        assert "session0" in session_ids
        assert "session1" in session_ids
        assert "session2" in session_ids

    def test_update_existing_session(self, temp_db):
        """Test updating an existing session"""
        storage = Storage(db_path=temp_db)

        # Create and save session
        session = Session(id="session1")
        storage.save_session(session)

        # Update and save again
        session.turn_count = 5
        task = Task(
            id="task1",
            title="New Task",
            description="New"
        )
        session.tasks["task1"] = task
        storage.save_session(session)

        # Load and verify
        loaded = storage.load_session("session1")
        assert loaded.turn_count == 5
        assert len(loaded.tasks) == 1
        assert loaded.tasks["task1"].title == "New Task"

    def test_save_session_with_agent(self, temp_db):
        """Test saving session with agent"""
        storage = Storage(db_path=temp_db)

        session = Session(id="session1")
        agent = Agent(
            id="agent1",
            name="Dev Agent",
            role=AgentRole.DEV,
            description="Developer",
            system_prompt="You are a dev"
        )
        session.agents["agent1"] = agent
        storage.save_session(session)

        # Load and verify
        loaded = storage.load_session("session1")
        assert len(loaded.agents) == 1
        assert loaded.agents["agent1"].name == "Dev Agent"
        assert loaded.agents["agent1"].role == AgentRole.DEV
