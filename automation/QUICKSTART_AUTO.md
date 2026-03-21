# 🚀 快速开始 - 自动化开发循环

## 📝 30 秒上手

### 前置要求检查清单

在开始之前，请确保：
- ✅ Claude Code CLI 已安装 (`claude --version` 可用)
- ✅ Python 3.10+ 已安装
- ✅ 项目依赖已安装 (`pip install -r requirements.txt`)
- ✅ Git 已配置 (`git config --list` 检查)
- ✅ 项目可以手动运行 (`python main.py` 成功启动)

### Windows 用户

```cmd
# 1. 进入 automation 目录
cd automation

# 2. 运行 5 次开发循环
run_dev_loop.bat 5
```

### Linux/macOS 用户

```bash
# 1. 进入 automation 目录
cd automation

# 2. 添加执行权限（首次运行）
chmod +x run_dev_loop.sh

# 3. 运行 5 次开发循环
./run_dev_loop.sh 5
```

---

## 🎯 它做什么？

每次循环自动执行：
1. ✅ 启动开发服务器
2. ✅ 调用 Claude Code AI 团队开发
3. ✅ 自动提交代码变更
4. ✅ 推送到 GitHub
5. ✅ 记录详细日志

### 详细流程说明

```
用户输入: ./run_dev_loop.sh 5
    ↓
第 1 轮开始
    ├─ 检查服务器状态 (如未运行则启动)
    ├─ 调用 Claude Code (--yes --no-interactive --allow-permissions)
    │   ├─ AI 分析 feature_list.json
    │   ├─ AI 选择下一个待办任务
    │   ├─ AI 编写/修改代码
    │   ├─ AI 运行测试
    │   └─ AI 更新任务状态
    ├─ 检测代码变更 (git diff)
    ├─ 自动提交 (git commit)
    └─ 自动推送 (git push)
    ↓
等待 5 秒...
    ↓
第 2 轮开始 (重复上述流程)
    ↓
... (共 5 轮)
    ↓
完成报告 (总耗时、成功次数等)
```

---

## 📊 查看进度

运行时会看到：
```
==================== 第 1/5 轮开发循环 ====================
[INFO] 检查服务器状态...
[STEP 1/3] 调用 Claude Code 执行开发任务...
[SUCCESS] 第 1 轮开发完成 (耗时: 5分18秒)
[STEP 2/3] 检查代码变更并提交...
[SUCCESS] 代码变更已提交: feat: 完成用户认证系统 (feat-008)
[SUCCESS] 代码已推送到远程仓库

进度: [████████░░░░░░░░░░] 20% (1/5)
```

### 进度条说明

- `░` 未完成的轮次
- `█` 已完成的轮次
- 百分比和当前轮次/总轮次

---

## 📁 查看日志

### 日志目录结构

```
logs/
├── dev_loop_20250321_143022.log       # 主日志（推荐优先查看）
├── server_20250321_143025.log          # 服务器启动日志
├── claude_1_20250321_143105.log        # 第1轮 Claude 执行日志
├── claude_2_20250321_143520.log        # 第2轮 Claude 执行日志
└── ...
```

### 实时查看日志

```bash
# 实时查看主日志（推荐）
tail -f logs/dev_loop_*.log

# 实时查看服务器日志
tail -f logs/server_*.log

# 查看最新的 Claude 执行日志
tail -f logs/claude_*.log | grep -E "\[INFO\]|\[ERROR\]|\[SUCCESS\]"
```

### 日志级别说明

- `[INFO]` - 一般信息（流程步骤、配置等）
- `[SUCCESS]` - 成功操作（任务完成、提交成功等）
- `[WARNING]` - 警告信息（非关键问题）
- `[ERROR]` - 错误信息（失败、异常等）
- `[STEP n/m]` - 进度步骤（当前步骤/总步骤数）

---

## 🛑 停止运行

### 优雅停止（推荐）

**Windows**: `Ctrl + C` → 等待当前轮完成

**Linux/macOS**: `Ctrl + C` → 等待当前轮完成

脚本会完成当前正在执行的一轮，然后生成报告并退出。

### 强制停止（不推荐）

**Windows**: `Ctrl + C` → 等待3秒 → 再次 `Ctrl + C`

**Linux/macOS**: `Ctrl + C` → 等待3秒 → 再次 `Ctrl + C`

会立即终止，可能导致代码未提交或服务器未正常关闭。

### 后台进程停止

```bash
# 查找进程
ps aux | grep run_dev_loop

# 终止进程
kill <PID>
```

---

## ⚙️ 高级用法

### 1. 自定义 Prompt

编辑脚本文件，找到 `INITIAL_PROMPT` 变量：

**run_dev_loop.sh (Linux/macOS)**:
```bash
INITIAL_PROMPT="请继续 SynergyAI 项目的开发工作..."
```

**run_dev_loop.bat (Windows)**:
```cmd
set INITIAL_PROMPT=请继续 SynergyAI 项目的开发工作...
```

#### 常用 Prompt 示例

```bash
# 专注于特定功能
INITIAL_PROMPT="请专注于开发用户认证模块，确保安全性测试通过。"

# 修复 Bug
INITIAL_PROMPT="请优先修复所有待修复的 Bug，不开发新功能。"

# 性能优化
INITIAL_PROMPT="请专注于性能优化，减少响应时间，提高吞吐量。"

# 测试覆盖
INITIAL_PROMPT="请提高测试覆盖率，确保核心功能都有单元测试。"

# 文档完善
INITIAL_PROMPT="请完善代码注释和 API 文档，提高可维护性。"
```

### 2. 修改循环次数

```bash
# 执行 1 轮（测试用）
./run_dev_loop.sh 1

# 执行 10 轮（小规模开发）
./run_dev_loop.sh 10

# 执行 50 轮（过夜开发）
./run_dev_loop.sh 50

# 执行 100 轮（周末开发）
./run_dev_loop.sh 100
```

### 3. 修改等待时间

编辑脚本，找到 `WAIT_TIME_BETWEEN_ROUNDS` 变量：

```bash
# 默认 5 秒
WAIT_TIME_BETWEEN_ROUNDS=5

# 改为 10 秒（给服务器更多恢复时间）
WAIT_TIME_BETWEEN_ROUNDS=10

# 改为 0 秒（连续执行，不等待）
WAIT_TIME_BETWEEN_ROUNDS=0
```

### 4. 后台运行（Linux/macOS）

```bash
# 基本后台运行
nohup ./run_dev_loop.sh 20 > logs/overnight.log 2>&1 &

# 查看后台任务
ps aux | grep run_dev_loop

# 查看输出
tail -f logs/overnight.log

# 停止后台任务
kill <PID>
```

### 5. 修改服务器端口

编辑脚本，找到 `SERVER_PORT` 变量：

```bash
# 默认 8000
SERVER_PORT=8000

# 改为 8080
SERVER_PORT=8080
```

---

## ⚠️ 注意事项

### 环境检查

1. **Claude Code CLI 已安装**
   ```bash
   claude --version
   # 应显示类似: claude 0.5.0
   ```

2. **Python 环境正常**
   ```bash
   python --version
   # 应显示: Python 3.10.x 或更高

   pip list | grep fastapi
   # 应显示 FastAPI 相关包
   ```

3. **Git 配置正确**
   ```bash
   git config user.name
   git config user.email
   git remote -v
   # 应显示远程仓库地址
   ```

4. **项目可以手动运行**
   ```bash
   # 在项目根目录
   python main.py
   # 服务器应成功启动在 http://localhost:8000
   ```

5. **API 密钥已配置**
   ```bash
   # Claude Code 应该可以访问 Anthropic API
   # 测试: claude --help
   ```

### 使用建议

1. **首次使用**: 先运行 1 轮，确保环境正常
2. **小规模测试**: 再运行 3-5 轮，观察 AI 工作质量
3. **规模化运行**: 确认无误后，可以运行更多轮
4. **定期检查**: 每隔几轮查看日志，确保开发方向正确
5. **代码审查**: 运行结束后，务必审查生成的代码

### 常见误区

❌ **错误做法**:
```bash
# 直接运行 100 轮，不检查环境
./run_dev_loop.sh 100
```

✅ **正确做法**:
```bash
# 先测试 1 轮
./run_dev_loop.sh 1

# 检查日志
cat logs/dev_loop_*.log

# 确认无误后运行更多轮
./run_dev_loop.sh 100
```

---

## 📚 详细文档

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [README.md](README.md) | 系统概述和功能介绍 | 所有用户 |
| [AUTO_DEV_GUIDE.md](AUTO_DEV_GUIDE.md) | 完整使用指南 | 进阶用户 |
| [FAQ.md](FAQ.md) | 常见问题解答 | 遇到问题的用户 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 故障排除指南 | 遇到错误的用户 |
| [BEST_PRACTICES.md](BEST_PRACTICES.md) | 最佳实践 | 希望优化的用户 |

---

## 🎉 开始使用

```bash
# 第一次运行，测试 1 轮
./run_dev_loop.sh 1

# 如果成功，查看日志
cat logs/dev_loop_*.log

# 确认无误，尝试更多轮
./run_dev_loop.sh 5

# 查看完成报告
# 脚本会自动显示统计信息
```

---

## 📞 获取帮助

如果遇到问题：
1. 查看 [FAQ.md](FAQ.md)
2. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. 查看日志文件: `logs/dev_loop_*.log`
4. 提交 Issue 到项目仓库

---

**SynergyAI** - 让 AI 团队协同工作 💪
