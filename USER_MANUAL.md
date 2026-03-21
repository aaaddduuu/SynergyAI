# 🤖 SynergyAI 用户使用手册

**版本**: 1.0.0
**更新时间**: 2026-03-22
**项目地址**: https://github.com/aaaddduuu/SynergyAI

---

## 📑 目录

1. [系统简介](#1-系统简介)
2. [快速开始](#2-快速开始)
3. [系统配置](#3-系统配置)
4. [功能详解](#4-功能详解)
5. [使用教程](#5-使用教程)
6. [API 文档](#6-api-文档)
7. [常见问题](#7-常见问题)
8. [最佳实践](#8-最佳实践)
9. [故障排除](#9-故障排除)

---

## 1. 系统简介

### 1.1 什么是 SynergyAI？

**SynergyAI** 是一个基于 LangGraph 的多智能体协作系统，通过模拟真实的 AI 团队协同工作，实现"1+1>2"的协同效应。

### 1.2 核心特性

#### 🤖 多智能体协作
- **6 种专业角色**: HR、PM、BA、Dev、QA、Architect
- **智能分工**: 每个角色专注于自己的专业领域
- **协同工作**: 智能体之间自动协调配合

#### 🎯 智能任务管理
- **自动创建任务**: AI 根据需求自动创建任务
- **智能分配**: 根据角色自动分配任务
- **状态跟踪**: 实时跟踪任务进度
- **优先级管理**: 自动排序任务优先级

#### 💬 实时通信
- **WebSocket 连接**: 毫秒级消息推送
- **Markdown 支持**: 丰富的格式化选项
- **代码高亮**: 自动识别和高亮代码

#### 📊 数据可视化
- **实时统计**: 团队效率、任务进度
- **图表展示**: 直观的图表分析
- **性能监控**: 系统性能实时监控

### 1.3 适用场景

- ✅ **项目管理**: 自动化项目管理和任务分配
- ✅ **需求分析**: 快速分析和整理需求
- ✅ **代码开发**: 辅助代码编写和代码审查
- ✅ **质量保证**: 自动化测试和问题发现
- ✅ **团队协作**: 模拟真实团队协作流程

---

## 2. 快速开始

### 2.1 环境要求

| 组件 | 要求 |
|------|------|
| Python | 3.10 或更高版本 |
| 操作系统 | Windows / macOS / Linux |
| 内存 | 最低 2GB，推荐 4GB+ |
| 网络 | 需要访问 LLM API |

### 2.2 安装步骤

#### 方式一：直接安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/aaaddduuu/SynergyAI.git
cd SynergyAI

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python main.py

# 4. 打开浏览器访问
# http://localhost:8000
```

#### 方式二：使用 Docker

```bash
# 1. 使用 Docker Compose 启动
docker-compose up -d

# 2. 访问应用
# http://localhost:8000
```

### 2.3 首次配置

1. **打开配置面板**
   - 点击右上角的 "⚙️ 配置" 按钮

2. **选择模型提供商**
   - **OpenAI**: GPT-4o、GPT-4o-mini、GPT-3.5-turbo
   - **Anthropic**: Claude 3.5 Sonnet、Claude 3 Opus
   - **智谱AI**: GLM-4、GLM-4-plus、GLM-4-flash

3. **输入 API Key**
   ```
   # OpenAI API Key 获取地址
   https://platform.openai.com/api-keys

   # Anthropic API Key 获取地址
   https://console.anthropic.com/

   # 智谱AI API Key 获取地址
   https://open.bigmodel.cn/usercenter/apikeys
   ```

4. **保存配置**
   - 点击 "保存配置" 按钮
   - 系统会自动验证 API Key

---

## 3. 系统配置

### 3.1 环境变量配置

创建 `.env` 文件（参考 `.env.example`）：

```bash
# ====================
# 应用基础配置
# ====================
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO

# ====================
# API 服务配置
# ====================
API_HOST=0.0.0.0
API_PORT=8000

# ====================
# LLM API 配置
# ====================
# OpenAI 配置
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic 配置
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# 智谱AI 配置
ZHIPU_API_KEY=your-zhipu-key-here

# ====================
# 安全配置
# ====================
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# CORS 配置
CORS_ORIGINS=http://localhost:8000,http://localhost:3000

# Rate Limiting（速率限制）
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CSRF 保护
CSRF_ENABLED=true

# ====================
# 数据库配置
# ====================
# 默认使用 SQLite，可选 PostgreSQL
DATABASE_URL=sqlite:///./data/synergyai.db
```

### 3.2 模型配置

在 Web 界面中配置：

1. **全局默认模型**
   ```
   设置 → 默认模型 → 选择模型
   ```

2. **角色专属模型**
   ```
   设置 → Agent 配置 → 为每个角色选择模型
   ```

3. **自定义模型**
   ```
   设置 → 自定义模型 → 输入模型名称和 API 端点
   ```

### 3.3 高级配置

#### 自定义智能体插件

```json
{
  "name": "数据分析师",
  "description": "专注于数据分析和可视化",
  "role": "data_analyst",
  "system_prompt": "你是一个专业的数据分析师...",
  "capabilities": ["数据分析", "图表生成", "报告撰写"]
}
```

#### 团队和项目管理

```
设置 → 团队管理 → 创建团队
设置 → 项目管理 → 创建项目
```

---

## 4. 功能详解

### 4.1 界面布局

```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI 协作团队          [对话轮数: 5] [进行中]       │
│  [⚙️配置] [📊统计] [➕新建项目]              [👤用户]  │
├────────────┬────────────────────────────────────────────┤
│            │                                            │
│  📋 侧边栏  │  💬 主聊天区域                           │
│            │  ────────────────                          │
│  📊 统计   │  [对话历史]                              │
│  ─────────  │  ────────────────                          │
│  • 任务进度│  👤 用户: 创建一个登录功能                 │
│  • 效率分析│  🤖 PM: 我来创建任务...                   │
│            │  🤖 Dev: 开始实现...                       │
│  👥 团队   │  🤖 QA: 测试通过...                       │
│  ─────────  │                                            │
│  • HR      │  [输入框]                                 │
│  • PM ✓   │  [发送]                                   │
│  • BA     │                                            │
│  • Dev    │                                            │
│  • QA     │                                            │
│  • Architect│                                           │
└────────────┴────────────────────────────────────────────┘
```

### 4.2 角色说明

| 角色 | 图标 | 职责 | 典型任务 |
|------|------|------|----------|
| **HR (人力资源)** | 🤝 | 团队协调、资源管理 | 人员安排、假期管理 |
| **PM (项目经理)** | 📊 | 项目管理、任务分配 | 需求分析、进度跟踪 |
| **BA (业务分析师)** | 📝 | 需求分析、文档编写 | 需求文档、规格说明 |
| **Dev (开发工程师)** | 💻 | 代码开发、功能实现 | 功能开发、Bug 修复 |
| **QA (测试工程师)** | 🧪 | 质量保证、测试验证 | 功能测试、回归测试 |
| **Architect (架构师)** | 🏛️ | 架构设计、技术决策 | 系统设计、技术选型 |

### 4.3 任务管理

#### 任务状态流转

```
pending (待办)
    ↓
in_progress (进行中)
    ↓
review (审核中)
    ↓
done (完成)

或

pending → blocked (阻塞) → pending
```

#### 任务优先级

| 优先级 | 说明 | 颜色标识 |
|--------|------|----------|
| **high** | 高优先级 | 🔴 红色 |
| **medium** | 中等优先级 | 🟡 黄色 |
| **low** | 低优先级 | 🟢 绿色 |

### 4.4 统计功能

#### 实时统计指标

- **对话轮数**: 当前会话的对话次数
- **任务总数**: 创建的任务数量
- **完成率**: 已完成任务占比
- **团队效率**: 各角色的工作效率

#### 统计图表

- **任务进度图**: 柱状图展示各状态任务数量
- **效率分析图**: 折线图展示团队效率趋势
- **时间线图**: 甘特图展示项目进度

---

## 5. 使用教程

### 5.1 创建第一个项目

#### 步骤 1: 新建项目

1. 点击右上角 "➕ 新建项目" 按钮
2. 系统自动创建新的会话
3. 顶部显示 "进行中" 状态

#### 步骤 2: 描述需求

在输入框中输入你的需求：

```
我想开发一个用户登录功能
```

#### 步骤 3: 观察协作

系统会自动：

1. **PM 接收需求**
   ```
   🤖 PM: 收到需求，我来分析一下...
        创建任务 "用户登录功能开发"
   ```

2. **BA 编写需求文档**
   ```
   🤖 BA: 我来编写需求规格说明...
        需求包括：
        - 用户名/密码登录
        - 记住密码功能
        - 密码加密存储
   ```

3. **Architect 设计架构**
   ```
   🤖 Architect: 技术方案建议：
        - 前端: React + TypeScript
        - 后端: FastAPI + SQLAlchemy
        - 数据库: PostgreSQL
   ```

4. **Dev 实现功能**
   ```
   🤖 Dev: 开始实现登录功能...
        [代码实现]
   ```

5. **QA 测试验证**
   ```
   🤖 QA: 执行功能测试...
        测试通过 ✅
   ```

### 5.2 常用命令

#### 任务管理命令

```
# 创建任务
"创建一个支付功能任务"
"PM, 创建新的任务"

# 分配任务
"把任务分配给 Dev"
"PM 分配登录任务给开发"

# 更新任务
"更新任务状态为进行中"
"将任务标记为完成"

# 查询任务
"显示所有任务"
"查看进行中的任务"
```

#### 角色交互命令

```
# 直接与特定角色对话
"PM, 当前项目进度如何？"
"Dev, 登录功能开发进度？"
"QA, 测试结果如何？"

# 请求建议
"Architect, 技术方案建议"
"BA, 帮我分析这个需求"
```

#### 系统命令

```
# 新建项目
"新建项目"
"创建新会话"

# 导出文档
"导出项目文档"
"生成项目报告"

# 统计查询
"显示项目统计"
"团队效率分析"
```

### 5.3 实战案例

#### 案例 1: 电商网站开发

```
用户: 我想开发一个电商网站

系统响应:
🤖 PM: 收到需求！电商网站是一个复杂的项目，
       我先来规划一下主要模块：
       1. 商品管理
       2. 购物车
       3. 订单系统
       4. 支付集成
       5. 用户系统

       正在创建任务...

🤖 Architect: 电商系统架构建议：
       - 前端: Next.js + TypeScript + Tailwind
       - 后端: FastAPI + Redis + PostgreSQL
       - 支付: Stripe API
       - 部署: Docker + AWS

🤖 Dev: 我可以先实现用户系统和商品管理模块。
       预计开发时间：2周

🤖 QA: 我会准备测试计划，
       包括功能测试、性能测试和安全测试
```

#### 案例 2: Bug 修复流程

```
用户: 登录功能有问题，密码重置不工作

系统响应:
🤖 QA: 收到 Bug 报告！我来验证问题...
       Bug 详情：
       - 功能: 密码重置
       - 问题描述: 重置邮件发送失败
       - 严重程度: 高

       正在创建 Bug 任务...

🤖 Dev: 收到 Bug 任务，我来检查代码...
       问题原因：邮件服务配置错误
       修复方案：更新 SMTP 配置
       正在修复...

🤖 Dev: 修复完成！已部署到测试环境

🤖 QA: 回归测试通过 ✅
       密码重置功能正常
```

#### 案例 3: 需求变更

```
用户: 我希望在登录页面添加微信登录

系统响应:
🤖 PM: 收到需求变更！我来评估影响...
       新增功能：微信登录
       影响范围：
       - 用户认证模块
       - 第三方集成
       - 用户体验优化

       正在更新需求文档...

🤖 BA: 更新需求规格说明：
       新增需求：
       - 微信扫码登录
       - 微信账号绑定
       - 登录状态同步

       技术要求：
       - 集成微信开放平台 API
       - OAuth 2.0 认证流程

🤖 Architect: 技术方案更新：
       新增组件：
       - 微信登录组件
       - OAuth 认证服务
       - 账号绑定服务

       数据库变更：
       - 新增社交账号表
       - 用户表扩展字段

🤖 Dev: 明白了，开始实现微信登录功能...
```

### 5.4 高级用法

#### 自定义工作流

创建自定义插件来扩展功能：

```python
# plugins/custom_agent.py
{
  "name": "安全专家",
  "description": "专注于代码安全审查",
  "role": "security_expert",
  "system_prompt": """你是一个代码安全专家，负责：
  1. 审查代码中的安全漏洞
  2. 提供安全最佳实践建议
  3. 验证安全修复方案""",
  "capabilities": [
    "安全审查",
    "漏洞扫描",
    "安全测试"
  ]
}
```

#### 批量任务创建

```
用户: 创建以下任务：
1. 用户注册
2. 用户登录
3. 密码重置
4. 个人资料编辑
5. 账号注销

系统响应:
🤖 PM: 收到批量任务请求！
       正在创建 5 个任务...

       ✅ 任务1: 用户注册 - 已分配给 Dev
       ✅ 任务2: 用户登录 - 已分配给 Dev
       ✅ 任务3: 密码重置 - 已分配给 Dev
       ✅ 任务4: 个人资料编辑 - 已分配给 Dev
       ✅ 任务5: 账号注销 - 已分配给 Dev

       所有任务已创建完成！
```

---

## 6. API 文档

### 6.1 WebSocket API

#### 连接地址

```
ws://localhost:8000/ws/chat
```

#### 消息格式

**客户端发送消息**

```json
{
  "type": "message",
  "content": "用户消息内容",
  "session_id": "会话ID（可选）"
}
```

**服务器响应**

```json
{
  "type": "message",
  "sender": "pm",
  "sender_role": "pm",
  "content": "消息内容",
  "timestamp": "2026-03-22T10:30:00",
  "task_id": "任务ID（可选）"
}
```

#### 消息类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `connected` | 连接成功 | - |
| `message` | 普通消息 | Agent 回复 |
| `task_update` | 任务更新 | 任务状态变化 |
| `typing` | 输入状态 | Agent 正在输入 |
| `error` | 错误消息 | 错误提示 |

### 6.2 REST API

#### 会话管理

**创建会话**

```http
POST /api/session
Content-Type: application/json

{}
```

**响应**

```json
{
  "session_id": "uuid-session-id",
  "created_at": "2026-03-22T10:30:00"
}
```

#### 任务管理

**获取任务列表**

```http
GET /api/tasks?session_id={session_id}
```

**创建任务**

```http
POST /api/tasks
Content-Type: application/json

{
  "title": "任务标题",
  "description": "任务描述",
  "priority": "high",
  "assignee_role": "dev"
}
```

**更新任务**

```http
PUT /api/tasks/{task_id}
Content-Type: application/json

{
  "state": "in_progress",
  "priority": "medium"
}
```

**删除任务**

```http
DELETE /api/tasks/{task_id}
```

#### 配置管理

**获取配置**

```http
GET /api/config
```

**保存配置**

```http
POST /api/config
Content-Type: application/json

{
  "provider": "openai",
  "model": "gpt-4o",
  "api_key": "sk-...",
  "agent_configs": {
    "pm": {
      "model": "gpt-4o",
      "temperature": 0.7
    }
  }
}
```

### 6.3 健康检查

```http
GET /api/health
```

**响应**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-22T10:30:00",
  "version": "1.0.0",
  "connections": 5
}
```

---

## 7. 常见问题

### 7.1 安装和启动问题

#### Q1: 启动时提示 "Module not found"

**问题**: 启动时报错 `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:

```bash
# 重新安装依赖
pip install -r requirements.txt --upgrade

# 如果还有问题，清理缓存后重装
pip cache purge
pip install -r requirements.txt
```

#### Q2: 端口 8000 被占用

**问题**: 启动时提示端口已被使用

**解决方案**:

```bash
# 方案 1: 修改端口
# 编辑 .env 文件
API_PORT=8001

# 方案 2: 停止占用端口的进程
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### 7.2 API 配置问题

#### Q3: API Key 验证失败

**问题**: 保存配置时提示 "API Key 验证失败"

**解决方案**:

1. **检查 API Key 是否正确**
   - 登录对应的平台确认 Key
   - 检查是否复制完整

2. **检查 API 是否可用**
   ```bash
   # 测试 OpenAI API
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **检查账户余额**
   - 确保账户有足够的额度

#### Q4: 模型响应很慢

**问题**: Agent 回复延迟很高

**解决方案**:

1. **更换更快的模型**
   ```
   GPT-4o-mini 比 GPT-4o 快 2-3 倍
   GLM-4-flash 比 GLM-4 快很多
   ```

2. **检查网络连接**
   ```bash
   # 测试 API 延迟
   ping api.openai.com
   ```

3. **调整并发设置**
   ```python
   # .env
   MAX_CONCURRENT_TASKS=3  # 降低并发数
   ```

### 7.3 使用问题

#### Q5: Agent 不回复

**问题**: 发送消息后没有 Agent 回复

**解决方案**:

1. **检查 WebSocket 连接状态**
   - 查看右上角的连接指示器
   - 绿色 = 已连接
   - 红色 = 未连接

2. **刷新页面重新连接**
   ```
   按 F5 刷新页面
   ```

3. **查看浏览器控制台**
   ```
   按 F12 打开开发者工具
   查看 Console 标签的错误信息
   ```

#### Q6: 任务状态不更新

**问题**: 创建的任务状态一直是 pending

**解决方案**:

1. **手动分配任务**
   ```
   "PM, 把任务分配给 Dev"
   ```

2. **检查 Agent 配置**
   ```
   设置 → Agent 配置 → 确保角色已启用
   ```

3. **刷新任务列表**
   ```
   点击任务列表的刷新按钮
   ```

### 7.4 性能问题

#### Q7: 内存占用过高

**问题**: 系统运行一段时间后内存占用很高

**解决方案**:

1. **清理旧会话**
   ```python
   # 运行清理脚本
   python clean_sessions.py
   ```

2. **限制会话数量**
   ```python
   # .env
   MAX_ACTIVE_SESSIONS=10
   ```

3. **重启服务**
   ```bash
   # 停止后重新启动
   python main.py
   ```

---

## 8. 最佳实践

### 8.1 需求描述技巧

#### ✅ 好的需求描述

```
我想开发一个用户登录功能，包括：
1. 用户名/密码登录
2. 记住密码功能
3. 忘记密码重置
4. 第三方登录（微信、QQ）

技术栈：React + FastAPI
```

#### ❌ 不好的需求描述

```
做一个登录
```

**为什么？**
- 太简短，缺乏细节
- 没有明确的功能范围
- 没有技术栈信息

### 8.2 任务管理建议

#### 优先级设置

| 优先级 | 适用场景 | 示例 |
|--------|----------|------|
| **high** | 核心功能、紧急Bug | 用户登录、支付功能 |
| **medium** | 重要功能、优化 | 个人资料、性能优化 |
| **low** | 锦上添花功能 | 主题切换、动画效果 |

#### 任务拆分

```
❌ 太大: "开发电商网站"
✅ 合理: "开发商品管理模块"
✅ 合理: "开发购物车功能"

✅ 更细: "实现商品列表 API"
✅ 更细: "实现商品详情页"
```

### 8.3 团队协作技巧

#### 充分利用各角色

```
# 需求分析阶段
"BA, 帮我分析这个需求是否完整？"
"Architect, 这个需求的技术可行性和工作量如何？"

# 开发阶段
"Dev, 实现方案有什么建议？"
"Architect, 这个设计有什么改进空间？"

# 测试阶段
"QA, 准备测试计划和测试用例"
"PM, 验收标准是什么？"
```

#### 明确指派任务

```
✅ 明确: "PM, 把登录任务分配给 Dev，优先级 high"
❌ 模糊: "谁来做登录？"
```

### 8.4 成本优化

#### 选择合适的模型

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 快速对话 | GPT-4o-mini | 速度快、成本低 |
| 代码生成 | GPT-4o | 质量高、能力强 |
| 需求分析 | Claude 3.5 Sonnet | 理解能力强 |
| 中文场景 | GLM-4 | 中文优化、成本低 |

#### 控制对话长度

```
✅ 好: 分段描述需求
❌ 差: 一次性描述所有需求
```

#### 定期清理

```bash
# 每周清理旧会话
python clean_sessions.py --days 7
```

---

## 9. 故障排除

### 9.1 日志查看

#### 应用日志

```bash
# 查看应用日志
tail -f logs/app.log

# 查看最近 100 行
tail -n 100 logs/app.log

# 搜索错误
grep ERROR logs/app.log
```

#### 安全日志

```bash
# 查看安全事件
tail -f logs/security.log

# 搜索 CSRF 相关
grep CSRF logs/security.log
```

### 9.2 数据库检查

#### 查看数据库状态

```bash
# 运行数据库检查脚本
python check_db.py

# 查看详细数据
python check_db2.py
```

#### 数据库备份

```bash
# 备份数据库
cp data/synergyai.db data/backup_$(date +%Y%m%d).db
```

### 9.3 性能监控

#### 查看性能统计

```bash
# 访问性能统计 API
curl http://localhost:8000/api/performance
```

#### 性能指标说明

| 指标 | 正常值 | 异常值 | 说明 |
|------|--------|--------|------|
| 平均响应时间 | < 500ms | > 1s | API 响应时间 |
| 内存占用 | < 1GB | > 2GB | 系统内存使用 |
| CPU 占用 | < 50% | > 80% | CPU 使用率 |
| WebSocket 连接数 | < 100 | > 500 | 并发连接数 |

### 9.4 常见错误码

| HTTP 状态码 | 说明 | 解决方案 |
|-------------|------|----------|
| 400 | 请求参数错误 | 检查请求格式 |
| 401 | 未认证 | 检查登录状态 |
| 403 | 权限不足 | 检查用户权限 |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器内部错误 | 查看日志 |

---

## 10. 附录

### 10.1 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息 |
| `Shift + Enter` | 换行 |
| `Esc` | 关闭弹窗 |
| `Ctrl + K` | 清空输入 |
| `Ctrl + /` | 打开配置 |

### 10.2 环境变量完整列表

```bash
# 应用配置
PYTHONUNBUFFERED=1          # Python 输出不缓冲
LOG_LEVEL=INFO              # 日志级别
DEBUG=False                 # 调试模式

# API 配置
API_HOST=0.0.0.0           # 监听地址
API_PORT=8000              # 监听端口

# LLM API
OPENAI_API_KEY=sk-...      # OpenAI API Key
ANTHROPIC_API_KEY=sk-ant-... # Anthropic API Key
ZHIPU_API_KEY=...          # 智谱AI API Key

# 安全配置
SECRET_KEY=...             # 应用密钥
JWT_SECRET_KEY=...         # JWT 密钥
CORS_ORIGINS=...           # CORS 允许源

# 限制配置
RATE_LIMIT_ENABLED=true    # 启用速率限制
CSRF_ENABLED=true          # 启用 CSRF 保护

# 数据库
DATABASE_URL=sqlite://...  # 数据库 URL
```

### 10.3 支持的资源

- **GitHub Issues**: https://github.com/aaaddduuu/SynergyAI/issues
- **文档仓库**: https://github.com/aaaddduuu/SynergyAI/tree/main/docs
- **更新日志**: CHANGELOG.md

### 10.4 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系支持

如果你在使用过程中遇到任何问题：

- 📧 Email: support@synergyai.com
- 💬 GitHub Issues: https://github.com/aaaddduuu/SynergyAI/issues
- 📖 文档: https://github.com/aaaddduuu/SynergyAI/wiki

---

**感谢使用 SynergyAI！** 🎉

Built with ❤️ using LangGraph + FastAPI
