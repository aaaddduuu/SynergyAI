# 🤖 SynergyAI 智能自动化开发系统

## 📖 概述

这是一个智能的自动化开发系统，可以从 `feature_list.json` 中自动领取任务并调用 Claude Code AI 团队完成开发工作。

## ✨ 核心特性

- ✅ **智能任务分配** - 按优先级自动选择待办任务
- ✅ **针对性 Prompt** - 为每个任务生成详细的开发指令
- ✅ **状态跟踪** - 实时更新任务状态到 feature_list.json
- ✅ **自动提交** - 每个任务完成后自动 git commit 和 push
- ✅ **详细日志** - 所有操作记录到 logs/ 目录
- ✅ **进度报告** - 实时显示开发进度和统计信息

## 🚀 快速开始

### Windows 用户

```cmd
# 进入 automation 目录
cd automation

# 执行 5 个任务
auto_dev.bat 5

# 执行所有任务（直到完成）
auto_dev.bat
```

### Python 直接运行

```bash
# 执行 5 个任务
python automation/auto_dev.py --iterations 5

# 执行所有任务
python automation/auto_dev.py
```

## 📋 工作流程

每次循环执行以下步骤：

```
1. 📋 从 feature_list.json 获取下一个待办任务
   ├─ 按优先级排序（高 > 中 > 低）
   └─ 选择状态为 "pending" 的任务

2. ✍️ 生成针对性的开发 Prompt
   ├─ 任务 ID 和标题
   ├─ 详细描述
   ├─ 任务步骤
   └─ 注意事项

3. 🤖 调用 Claude Code 执行开发
   ├─ 传递项目目录和 Prompt
   └─ 设置 1 小时超时

4. 📝 更新任务状态
   └─ 从 "pending" → "in_progress" → "done"

5. 📤 自动提交和推送
   ├─ git add -A
   ├─ git commit（生成规范的 commit message）
   └─ git push origin main

6. 📊 显示进度报告
   ├─ 总任务数 / 已完成数
   ├─ 完成百分比
   └─ 剩余任务列表

7. ⏱️ 等待 10 秒后继续下一个任务
```

## 📊 日志和监控

### 日志文件位置

```
logs/
├── auto_dev_20250321_143022.log    # 自动化开发日志
├── dev_loop_20250321_143022.log    # 开发循环日志
└── server_20250321_143022.log      # 服务器日志
```

### 查看实时日志

**Windows PowerShell:**
```powershell
Get-Content logs\auto_dev_*.log -Wait -Tail 50
```

**Linux/macOS:**
```bash
tail -f logs/auto_dev_*.log
```

### 日志内容示例

```
[2025-03-21 14:30:22] ================================================================================
[2025-03-21 14:30:22] 开始处理任务: 修复配置加载 Bug
[2025-03-21 14:30:22] 任务ID: feat-001
[2025-03-21 14:30:22] 描述: 前端加载配置时偶尔报错，需要修复配置加载逻辑
[2025-03-21 14:30:22] ================================================================================
[2025-03-21 14:30:22] 任务 feat-001 标记为进行中
[2025-03-21 14:30:22] ================================================================================
[2025-03-21 14:30:22] 调用 Claude Code 执行开发任务...
[2025-03-21 14:30:22] ================================================================================
...
[2025-03-21 14:45:30] Claude Code 执行成功
[2025-03-21 14:45:30] 代码变更已提交
[2025-03-21 14:45:35] 代码已推送到远程仓库
[2025-03-21 14:45:35] 任务 feat-001 标记为完成
[2025-03-21 14:45:35] ================================================================================
[2025-03-21 14:45:35] 当前进度: 1/20 (5%)
[2025-03-21 14:45:35] ================================================================================
```

## 📁 项目结构

```
ai-coworker/
├── automation/
│   ├── auto_dev.py              # Python 自动化脚本
│   ├── auto_dev.bat             # Windows 批处理启动器
│   ├── feature_list.json        # 功能清单（待办任务）
│   └── logs/                    # 日志目录
├── core/
│   ├── features.py              # 功能清单管理系统
│   ├── agents.py                # AI Agent 定义
│   └── orchestrator.py          # 任务编排器
└── main.py                      # FastAPI 服务器
```

## ⚙️ 配置说明

### 修改每次循环等待时间

编辑 `automation/auto_dev.py`，找到这一行：

```python
time.sleep(10)  # 等待 10 秒
```

改成你想要的秒数。

### 修改 Claude Code 超时时间

编辑 `automation/auto_dev.py`，找到：

```python
timeout=3600  # 1小时超时
```

可以根据任务复杂度调整。

### 自定义 Prompt 模板

编辑 `automation/auto_dev.py` 中的 `generate_prompt()` 方法：

```python
def generate_prompt(self, feature) -> str:
    prompt = f"""你的自定义 prompt 内容...

    【任务ID】{feature.id}
    【任务标题】{feature.title}
    ...
    """
    return prompt
```

## 🎯 任务优先级

系统按以下顺序选择任务：

1. 🔴 **高优先级** (high) - 最先执行
2. 🟡 **中优先级** (medium)
3. 🟢 **低优先级** (low) - 最后执行

同优先级的任务按在 `feature_list.json` 中的顺序执行。

## 📈 进度跟踪

### 查看 feature_list.json

```json
{
  "features": [
    {
      "id": "feat-001",
      "status": "done",        // ✅ 已完成
      "title": "修复配置加载 Bug"
    },
    {
      "id": "feat-002",
      "status": "pending",     // ⏸️ 待处理
      "title": "Docker 部署配置"
    },
    {
      "id": "feat-003",
      "status": "in_progress", // ▶️ 进行中
      "title": "Swagger API 文档"
    }
  ],
  "statistics": {
    "total": 20,
    "by_status": {
      "pending": 18,
      "in_progress": 1,
      "done": 1
    }
  }
}
```

### Python 代码查询进度

```python
from core.features import FeatureList

fl = FeatureList()
print(fl.get_progress_summary())
print(fl.generate_report())
```

## 🛑 停止运行

**Windows:** `Ctrl + C`

**Linux/macOS:** `Ctrl + C`

脚本会优雅地停止，已完成的工作会保存。

## ⚠️ 注意事项

### 1. Claude Code CLI 必须已安装

```bash
# 检查安装
claude --version

# 如果未安装，访问
https://claude.ai/code
```

### 2. Git 必须配置好认证

```bash
# 测试推送
git push origin main

# 如果需要认证，配置
git config --global credential.helper store
```

### 3. Python 依赖

确保项目依赖已安装：

```bash
pip install -r requirements.txt
```

### 4. 网络连接

Claude Code 需要网络连接到 Anthropic API。

## 🔧 故障排除

### 问题 1: `python: command not found`

**解决:** 安装 Python 3.7+
- Windows: https://python.org/downloads/
- 添加 Python 到 PATH 环境变量

### 问题 2: `claude: command not found`

**解决:** 安装 Claude Code CLI
- 访问: https://claude.ai/code
- 下载并安装

### 问题 3: Git 推送失败

**解决:** 配置 Git 认证
```bash
git config --global credential.helper store
git push origin main
# 输入用户名和密码（或 Personal Access Token）
```

### 问题 4: 任务执行超时

**解决:** 增加 timeout 值
```python
# 在 auto_dev.py 中
timeout=7200  # 2小时
```

### 问题 5: feature_list.json 未更新

**解决:** 检查文件权限
```bash
# 确保 feature_list.json 可写
chmod +w feature_list.json  # Linux/macOS
```

## 📚 相关文档

- [AUTO_DEV_GUIDE.md](AUTO_DEV_GUIDE.md) - 详细开发指南
- [QUICKSTART_AUTO.md](QUICKSTART_AUTO.md) - 快速开始
- [REFERENCE.md](REFERENCE.md) - 参考文档

## 🎉 开始使用

```cmd
# 第一次运行，测试 1 个任务
cd automation
auto_dev.bat 1

# 如果成功，可以运行更多任务
auto_dev.bat 5

# 或者运行所有任务
auto_dev.bat
```

---

**SynergyAI** - 让 AI 团队协同工作 💪
