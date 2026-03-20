import uuid
import json
from typing import TypedDict, Annotated, Sequence, Optional, Literal, List, Dict, Any
from datetime import datetime
import operator
from pathlib import Path

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.storage import Session, Message, Task, TaskState, AgentRole, MessageType
from core.agents import get_agent_prompt, AGENT_SYSTEM_PROMPTS, TaskOperation
from core.model_config import model_config_manager, create_llm_for_config
from core.features import FeatureList


class AgentState(TypedDict):
    session: Session
    messages: Sequence[BaseMessage]
    current_agent: Optional[str]
    pending_approval: Optional[dict]
    task_updates: list


class MultiAgentOrchestrator:
    def __init__(self, llm=None, model: str = "gpt-4", api_key: str = None, base_url: str = None, project_dir: str = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

        if llm:
            self.llm = llm
        else:
            if base_url:
                self.llm = ChatOpenAI(
                    model=model,
                    api_key=api_key or "dummy",
                    base_url=base_url
                )
            else:
                self.llm = ChatOpenAI(
                    model=model,
                    api_key=api_key or "sk-dummy"
                )

        # 初始化功能清单
        self.feature_list = FeatureList(project_dir)

        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        
        graph.add_node("route_message", self.route_message)
        graph.add_node("hr_agent", self.hr_node)
        graph.add_node("pm_agent", self.pm_node)
        graph.add_node("ba_agent", self.ba_node)
        graph.add_node("dev_agent", self.dev_node)
        graph.add_node("qa_agent", self.qa_node)
        graph.add_node("architect_agent", self.architect_node)
        graph.add_node("execute_task_operations", self.execute_task_operations)
        graph.add_node("check_approval", self.check_approval_node)
        graph.add_node("check_session_end", self.check_session_end)
        
        graph.set_entry_point("route_message")
        
        graph.add_conditional_edges(
            "route_message",
            self.route_to_agent,
            {
                "hr": "hr_agent",
                "pm": "pm_agent", 
                "ba": "ba_agent",
                "dev": "dev_agent",
                "qa": "qa_agent",
                "architect": "architect_agent",
                "orchestrator": "check_session_end"
            }
        )
        
        for agent in ["hr_agent", "pm_agent", "ba_agent", "dev_agent", "qa_agent", "architect_agent"]:
            graph.add_edge(agent, "execute_task_operations")
        
        graph.add_edge("execute_task_operations", "check_approval")
        
        graph.add_conditional_edges(
            "check_approval",
            self.should_request_approval,
            {
                "continue": "check_session_end",
                "approval": "check_session_end"
            }
        )
        
        graph.add_edge("check_session_end", END)
        
        return graph.compile()
    
    def route_message(self, state: AgentState) -> AgentState:
        """Determine which agent should handle the message"""
        session = state["session"]
        messages = state["messages"]
        
        if not messages:
            state["current_agent"] = "hr"
            return state
        
        last_message = messages[-1]
        if isinstance(last_message, HumanMessage):
            content = last_message.content.lower()
            
            if any(kw in content for kw in ["招聘", "人力", "增加", "人员", "简历", "面试", "请假", "离职", "团队"]):
                state["current_agent"] = "hr"
            elif any(kw in content for kw in ["进度", "任务", "分配", "管理", "项目", "进度", "安排", "截止"]):
                state["current_agent"] = "pm"
            elif any(kw in content for kw in ["需求", "功能", "分析", "文档", "spec", "specification", "业务"]):
                state["current_agent"] = "ba"
            elif any(kw in content for kw in ["开发", "代码", "实现", "功能", "bug", "修复", "技术"]):
                state["current_agent"] = "pm"
            elif any(kw in content for kw in ["测试", "验证", "qa", "test", "质量"]):
                state["current_agent"] = "qa"
            elif any(kw in content for kw in ["架构", "设计", "技术选型", "方案", "架构师"]):
                state["current_agent"] = "architect"
            else:
                state["current_agent"] = "pm"
        
        return state
    
    def route_to_agent(self, state: AgentState) -> Literal["hr", "pm", "ba", "dev", "qa", "architect", "orchestrator"]:
        """Route to the appropriate agent"""
        return state.get("current_agent", "pm")
    
    def _create_agent_llm(self, role: AgentRole) -> Any:
        """Create LLM instance with agent-specific config"""
        config = model_config_manager.get_config_for_role(role.value)
        return create_llm_for_config(config)
    
    def _get_task_info(self, session: Session, role: AgentRole = None) -> str:
        """Get formatted task information for the agent"""
        # 首先添加进度摘要（帮助 Agent 快速了解之前的工作）
        progress_summary = session.get_progress_summary()
        task_info = f"\n## 📋 项目进度摘要\n{progress_summary}\n"

        # 添加功能清单信息（帮助 Agent 了解整体功能需求）
        feature_summary = self.feature_list.get_progress_summary()
        task_info += f"\n{feature_summary}\n"

        # 显示下一个待办功能
        next_feature = self.feature_list.get_next_feature(role.value if role else None)
        if next_feature:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(next_feature.priority, "⚪")
            task_info += f"\n## 🎯 建议下一个功能\n"
            task_info += f"{priority_icon} **{next_feature.title}**\n"
            task_info += f"- 描述: {next_feature.description}\n"
            task_info += f"- 负责人: {next_feature.assignee_role}\n"
            task_info += f"- 状态: {next_feature.status}\n"
        elif role == AgentRole.PM:
            task_info += f"\n## 🎯 建议下一步\n"
            task_info += "请查看功能清单（feature_list.json）选择下一个待开发功能。\n"

        # 显示当前任务列表
        if not session.tasks:
            task_info += "\n## 当前任务列表\n暂无任务"
        else:
            if role == AgentRole.DEV:
                task_info += "\n## 你的任务列表\n"
                for task in session.tasks.values():
                    if task.assignee_role == AgentRole.DEV:
                        task_info += f"- [{task.state.value}] {task.title}\n"
            elif role == AgentRole.QA:
                task_info += "\n## 待测试任务\n"
                for task in session.tasks.values():
                    if task.state == TaskState.REVIEW:
                        task_info += f"- {task.title} (开发: {task.assignee})\n"
            else:
                task_info += "\n## 当前任务列表\n"
                for task in session.tasks.values():
                    task_info += f"- [{task.state.value}] {task.title} (负责人: {task.assignee or '未分配'})\n"

        return task_info
    
    def hr_node(self, state: AgentState) -> AgentState:
        """HR Agent processing"""
        session = state["session"]
        messages = state["messages"]
        
        hr_llm = self._create_agent_llm(AgentRole.HR)
        
        system_msg = SystemMessage(content=AGENT_SYSTEM_PROMPTS[AgentRole.HR])
        agent_messages = [system_msg] + list(messages)
        
        response = hr_llm.invoke(agent_messages)
        
        msg = Message(
            id=str(uuid.uuid4()),
            sender="HR",
            sender_role="hr",
            content=response.content,
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        
        state["messages"] = list(messages) + [response]
        
        return state
    
    def pm_node(self, state: AgentState) -> AgentState:
        """PM Agent processing"""
        session = state["session"]
        messages = state["messages"]
        
        pm_llm = self._create_agent_llm(AgentRole.PM)
        
        task_info = self._get_task_info(session, AgentRole.PM)
        
        system_content = AGENT_SYSTEM_PROMPTS[AgentRole.PM] + f"\n\n{task_info}"
        system_msg = SystemMessage(content=system_content)
        agent_messages = [system_msg] + list(messages)
        
        response = pm_llm.invoke(agent_messages)
        
        msg = Message(
            id=str(uuid.uuid4()),
            sender="项目经理",
            sender_role="pm",
            content=response.content,
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        
        state["messages"] = list(messages) + [response]
        
        return state
    
    def ba_node(self, state: AgentState) -> AgentState:
        """BA Agent processing"""
        session = state["session"]
        messages = state["messages"]
        
        ba_llm = self._create_agent_llm(AgentRole.BA)
        
        task_info = self._get_task_info(session, AgentRole.BA)
        
        system_content = AGENT_SYSTEM_PROMPTS[AgentRole.BA] + f"\n\n{task_info}"
        system_msg = SystemMessage(content=system_content)
        agent_messages = [system_msg] + list(messages)
        
        response = ba_llm.invoke(agent_messages)
        
        msg = Message(
            id=str(uuid.uuid4()),
            sender="业务分析师",
            sender_role="ba",
            content=response.content,
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        
        state["messages"] = list(messages) + [response]
        
        return state
    
    def dev_node(self, state: AgentState) -> AgentState:
        """Dev Agent processing"""
        session = state["session"]
        messages = state["messages"]
        
        dev_llm = self._create_agent_llm(AgentRole.DEV)
        
        task_info = self._get_task_info(session, AgentRole.DEV)
        
        system_content = AGENT_SYSTEM_PROMPTS[AgentRole.DEV] + f"\n\n{task_info}"
        system_msg = SystemMessage(content=system_content)
        agent_messages = [system_msg] + list(messages)
        
        response = dev_llm.invoke(agent_messages)
        
        msg = Message(
            id=str(uuid.uuid4()),
            sender="开发工程师",
            sender_role="dev",
            content=response.content,
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        
        state["messages"] = list(messages) + [response]
        
        return state
    
    def qa_node(self, state: AgentState) -> AgentState:
        """QA Agent processing"""
        session = state["session"]
        messages = state["messages"]
        
        qa_llm = self._create_agent_llm(AgentRole.QA)
        
        task_info = self._get_task_info(session, AgentRole.QA)
        
        system_content = AGENT_SYSTEM_PROMPTS[AgentRole.QA] + f"\n\n{task_info}"
        system_msg = SystemMessage(content=system_content)
        agent_messages = [system_msg] + list(messages)
        
        response = qa_llm.invoke(agent_messages)
        
        msg = Message(
            id=str(uuid.uuid4()),
            sender="测试工程师",
            sender_role="qa",
            content=response.content,
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        
        state["messages"] = list(messages) + [response]
        
        return state
    
    def architect_node(self, state: AgentState) -> AgentState:
        """Architect Agent processing"""
        session = state["session"]
        messages = state["messages"]
        
        arch_llm = self._create_agent_llm(AgentRole.ARCHITECT)
        
        system_msg = SystemMessage(content=AGENT_SYSTEM_PROMPTS[AgentRole.ARCHITECT])
        agent_messages = [system_msg] + list(messages)
        
        response = arch_llm.invoke(agent_messages)
        
        msg = Message(
            id=str(uuid.uuid4()),
            sender="架构师",
            sender_role="architect",
            content=response.content,
            message_type=MessageType.AGENT
        )
        session.add_message(msg)
        
        state["messages"] = list(messages) + [response]
        
        return state
    
    def execute_task_operations(self, state: AgentState) -> AgentState:
        """Execute task operations found in the agent's response"""
        session = state["session"]
        task_updates = []

        last_msg = session.messages[-1] if session.messages else None
        if not last_msg or last_msg.message_type != MessageType.AGENT:
            return state

        content = last_msg.content
        operations = TaskOperation.parse(content)

        # 记录任务操作统计
        operations_summary = {
            "created": 0,
            "updated": 0,
            "assigned": 0,
            "deleted": 0
        }

        for op in operations:
            try:
                if op['action'] == 'create':
                    task = Task(
                        id=str(uuid.uuid4()),
                        title=op['title'],
                        description=op['description'],
                        assignee_role=AgentRole(op['assignee_role']),
                        priority=op['priority'],
                        created_by="agent"
                    )
                    session.tasks[task.id] = task
                    task_updates.append(f"创建任务: {op['title']}")
                    operations_summary["created"] += 1

                elif op['action'] == 'update_state':
                    for task in session.tasks.values():
                        if task.title == op['title']:
                            task.state = TaskState(op['state'])
                            task.updated_at = datetime.now()
                            task_updates.append(f"更新任务 '{op['title']}' 状态为: {op['state']}")
                            operations_summary["updated"] += 1
                            break

                elif op['action'] == 'assign':
                    for task in session.tasks.values():
                        if task.title == op['title']:
                            task.assignee_role = AgentRole(op['assignee_role'])
                            task.updated_at = datetime.now()
                            task_updates.append(f"分配任务 '{op['title']}' 给: {op['assignee_role']}")
                            operations_summary["assigned"] += 1
                            break

                elif op['action'] == 'delete':
                    for task_id, task in list(session.tasks.items()):
                        if task.title == op['title']:
                            del session.tasks[task_id]
                            task_updates.append(f"删除任务: {op['title']}")
                            operations_summary["deleted"] += 1
                            break
            except Exception as e:
                task_updates.append(f"操作失败: {str(e)}")

        state["task_updates"] = task_updates

        if task_updates:
            update_msg = Message(
                id=str(uuid.uuid4()),
                sender="系统",
                sender_role="system",
                content="任务操作已执行:\n" + "\n".join(task_updates),
                message_type=MessageType.TASK_UPDATE
            )
            session.add_message(update_msg)

            # 记录到进度日志（解决上下文恢复困难）
            current_agent = state.get("current_agent", "unknown")
            work_summary = f"完成了 {len(task_updates)} 个任务操作:\n" + "\n".join(f"- {update}" for update in task_updates)

            # 添加额外的进度信息
            additional_info = {
                "任务创建": operations_summary["created"],
                "任务更新": operations_summary["updated"],
                "任务分配": operations_summary["assigned"],
                "任务删除": operations_summary["deleted"]
            }

            session.update_progress_log(
                agent_role=current_agent,
                work_done=work_summary,
                additional_info=additional_info
            )

        return state
    
    def check_approval_node(self, state: AgentState) -> AgentState:
        """Check if approval is needed"""
        session = state["session"]
        
        last_msg = session.messages[-1] if session.messages else None
        if last_msg and "[REQUEST]" in last_msg.content:
            state["pending_approval"] = {
                "type": "user_approval",
                "content": last_msg.content
            }
        else:
            state["pending_approval"] = None
        
        return state
    
    def should_request_approval(self, state: AgentState) -> Literal["continue", "approval"]:
        """Determine if we need user approval"""
        if state.get("pending_approval"):
            return "approval"
        return "continue"
    
    def check_session_end(self, state: AgentState) -> AgentState:
        """Check if session should end"""
        session = state["session"]
        
        should_end, reason = session.check_session_end()
        
        if should_end:
            if reason == "task_completed":
                msg = "任务已完成！现在我需要提交离职申请。如果有未完成的任务，我会生成交接文档。"
            else:
                msg = "我们已经交流了30轮，session即将结束。我会提交离职并生成交接文档。"
            
            handover_doc = session.generate_handover_doc()
            session.handover_doc = handover_doc
            session.is_active = False
            
            end_message = Message(
                id=str(uuid.uuid4()),
                sender="系统",
                sender_role="system",
                content=msg + "\n\n" + handover_doc,
                message_type=MessageType.SYSTEM
            )
            session.add_message(end_message)
        
        return state
    
    def chat(self, session: Session, user_message: str) -> Message:
        """Process a chat message"""
        msg = Message(
            id=str(uuid.uuid4()),
            sender="用户",
            sender_role="user",
            content=user_message,
            message_type=MessageType.USER
        )
        session.add_message(msg)
        
        messages = [HumanMessage(content=user_message)]
        
        initial_state: AgentState = {
            "session": session,
            "messages": messages,
            "current_agent": None,
            "pending_approval": None,
            "task_updates": []
        }
        
        result = self.graph.invoke(initial_state)
        
        return session.messages[-1]
