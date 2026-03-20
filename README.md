# 🤖 SynergyAI - 多智能体协作平台 | Multi-Agent Collaboration Platform

[English](#english) | [中文](#中文)

---

## ⭐ Features | 功能特点

### 🚀 Multi-Agent Collaboration | 多智能体协作

- **6 Professional Roles | 6种专业角色**: HR, PM, BA, Dev, QA, Architect
- **Real-time Communication | 实时通信**: WebSocket-powered instant messaging
- **Task Automation | 任务自动化**: AI agents can create, assign, and complete tasks autonomously

### 🎯 Smart Task Management | 智能任务管理

- **State Tracking | 状态跟踪**: pending → in_progress → review → done
- **Role-based Assignment | 角色分配**: Tasks auto-assigned to appropriate roles
- **Progress Visualization | 进度可视化**: Real-time progress bars and statistics

### 🔧 Flexible Model Configuration | 灵活的模型配置

- **Multiple Providers | 多供应商支持**: OpenAI, Anthropic, 智谱AI (Zhipu), Custom
- **Per-Role Models | 角色独立模型**: Each agent can use different models
- **Easy Setup | 轻松配置**: User-friendly UI for API key management

### 💻 Modern Web Interface | 现代 Web 界面

- **Real-time Updates | 实时更新**: Live message delivery and task sync
- **Markdown Support | Markdown 支持**: Code highlighting, formatting, and more
- **Responsive Design | 响应式设计**: Works on desktop and mobile

---

## 🏗️ Architecture | 架构

```
User → WebUI ←→ FastAPI ←→ Orchestrator ←→ [HR, PM, BA, Dev, QA, Architect]
                                              ↓
                                           SQLite
```

---

## 🚀 Quick Start | 快速开始

### Prerequisites | 环境要求

```bash
Python 3.10+
```

### Installation | 安装

```bash
# Clone the repository | 克隆仓库
git clone https://github.com/aaaddduuu/SynergyAI.git
cd SynergyAI

# Install dependencies | 安装依赖
pip install -r requirements.txt

# Start the server | 启动服务
python main.py
```

### Configuration | 配置

1. Open http://localhost:8000
2. Click the **Settings** button (⚙️)
3. Select your model provider:
   - **OpenAI**: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
   - **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
   - **智谱AI**: GLM-4, GLM-4-plus, GLM-4-flash
4. Enter your API key
5. Click **Save** | 点击保存

### Usage | 使用

1. Click **"新建项目"** to create a new session
2. Start chatting with the AI team
3. Try commands like:
   - "创建一个用户登录任务" (Create a user login task)
   - "PM 分配任务给开发" (PM assigns task to Dev)
   - "开发完成后提交测试" (Dev submits for testing)

---

## 📖 Role Descriptions | 角色说明

| Role | 角色 | Description | 说明 |
|------|------|-------------|------|
| 🤝 HR | 人力资源 | Coordinates with leadership, manages hiring/leave requests | 与管理层协调，管理招聘/请假请求 |
| 📊 PM | 项目经理 | Manages project progress, assigns tasks, reports status | 管理项目进度，分配任务，汇报状态 |
| 📝 BA | 业务分析师 | Analyzes requirements, writes specifications | 分析需求，编写规格说明 |
| 💻 Dev | 开发工程师 | Implements features, fixes bugs | 实现功能，修复缺陷 |
| 🧪 QA | 测试工程师 | Tests functionality, validates requirements | 测试功能，验证需求 |
| 🏛️ Architect | 架构师 | Designs system architecture, makes technical decisions | 设计系统架构，做技术决策 |

---

## � API Endpoints | API 接口

| Method | Endpoint | Description | 说明 |
|--------|----------|-------------|------|
| GET | `/` | Web UI | Web 界面 |
| WebSocket | `/ws/chat` | Real-time chat | 实时聊天 |
| POST | `/api/session` | Create session | 创建会话 |
| GET | `/api/tasks` | List tasks | 获取任务列表 |
| POST | `/api/tasks` | Create task | 创建任务 |
| PUT | `/api/tasks/{id}` | Update task | 更新任务 |
| GET | `/api/config` | Get config | 获取配置 |
| POST | `/api/config` | Save config | 保存配置 |

---

## 🛠️ Tech Stack | 技术栈

- **Backend**: FastAPI, LangGraph, LangChain
- **LLM Providers**: OpenAI, Anthropic, 智谱AI (Zhipu)
- **Database**: SQLite
- **Frontend**: HTML, TailwindCSS, Vanilla JS

---

## 📸 Screenshots | 截图

```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI Coworker Team                    [Settings] ⚙️  │
├────────────┬────────────────────────────────────────────┤
│            │                                            │
│  📋 Tasks  │  💬 Chat Area                             │
│  ─────────  │  ────────────────                          │
│  □ Login   │  👤 User: 创建登录功能                     │
│  □ Register│  🤖 PM: 已创建任务"用户登录"                │
│            │  🤖 Dev: 开始开发...                       │
│  👥 Team   │  🤖 QA: 测试中...                          │
│  ─────────  │                                            │
│  HR         │  ┌────────────────────────────────────┐  │
│  PM ✓       │  │ Type message...              [Send] │  │
│  BA         │  └────────────────────────────────────┘  │
│  Dev        │                                            │
└────────────┴────────────────────────────────────────────┘
```

---

## 🤝 Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请提交 Pull Request。

---

## 📄 License | 许可证

MIT License

---

## ⭐ Show Your Support | 支持我们

If you find this project helpful, please give us a ⭐!

如果觉得 SynergyAI 有用，请给我们一个 ⭐！

---

<p align="center">
  <b>Built with ❤️ using LangGraph + FastAPI</b>
</p>

---

## 🌟 项目名称寓意

**SynergyAI** = **Synergy**（协同效应）+ **AI**

> "The whole is greater than the sum of its parts"
> — Aristotle

多个 AI Agent 协作产生的效果大于单独工作之和，这就是协同效应。

---

## 中文

### 这是什么？

**SynergyAI** 是一个基于 LangGraph 的多智能体协作系统，通过 AI 团队协同工作产生 1+1>2 的效应。

### 核心功能

1. **多智能体协作**: 6种专业角色，模拟真实团队
2. **智能任务管理**: 自动创建、分配、跟踪任务
3. **灵活模型配置**: 支持 OpenAI、Anthropic、智谱AI
4. **实时通信**: WebSocket 实时消息推送
5. **现代界面**: 美观易用的 Web UI

### 开始使用

```bash
pip install -r requirements.txt
python main.py
# 打开 http://localhost:8000
```

### 配置模型

1. 点击右上角 **设置** 按钮
2. 选择模型供应商（OpenAI/智谱AI/Anthropic）
3. 输入 API Key
4. 点击保存

### 与 AI 团队互动

- "创建一个用户登录任务"
- "PM 分配任务给开发"
- "开发完成后提交测试"
- "QA 审核通过"

---

<p align="center">
  <sub>Made with ❤️ using LangGraph + FastAPI</sub>
</p>
