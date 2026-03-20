# 🤖 SynergyAI 自动化开发系统

这个文件夹包含了 SynergyAI 项目的自动化开发循环系统，可以循环调用 Claude Code 执行完整的开发流程。

---

## 📁 文件结构

```
automation/
├── README.md                      # 本文件
├── run_dev_loop.sh                # Shell 脚本（Linux/macOS）
├── run_dev_loop.bat               # 批处理脚本（Windows）
├── dev_loop_config.example.sh      # 配置示例
├── QUICKSTART_AUTO.md             # 30秒快速开始指南
├── AUTO_DEV_GUIDE.md              # 完整使用指南
└── AUTO_DEV_SUMMARY.md            # 功能总结
```

---

## 🚀 快速开始

### Windows 用户

```cmd
# 在项目根目录执行
cd automation
run_dev_loop.bat 5
```

### Linux/macOS 用户

```bash
# 在项目根目录执行
cd automation
./run_dev_loop.sh 5
```

---

## ✨ 核心功能

### 自动化流程

每轮循环自动执行：

1. ✅ **启动/检查开发服务器**
   - 自动启动 FastAPI 服务器
   - 健康检查

2. ✅ **调用 Claude Code AI 团队**
   - 发送初始 Prompt
   - 自动确认所有权限
   - 执行开发任务

3. ✅ **代码管理**
   - 检测代码变更
   - 自动提交（git commit）
   - 自动推送（git push）

4. ✅ **日志记录**
   - 详细的进度日志
   - 分类日志文件
   - 完成报告

### 智能权限处理

使用以下参数确保无人工介入：

- `--yes` - 自动确认所有提示
- `--no-interactive` - 非交互模式
- `--allow-permissions` - 允许所有权限（文件读写、执行命令等）

### 完整的日志系统

```
logs/
├── dev_loop_20250321_010000.log       # 主日志
├── server_20250321_010005.log          # 服务器日志
├── claude_1_20250321_010105.log        # 第1轮 Claude 日志
├── claude_2_20250321_010520.log        # 第2轮 Claude 日志
└── ...
```

---

## 📊 使用示例

### 基础用法

```bash
# 执行 5 次开发循环
./run_dev_loop.sh 5
```

### 高级用法

```bash
# 过夜开发（50 轮）
nohup ./run_dev_loop.sh 50 > ../../logs/overnight.log 2>&1 &

# 修改 Prompt 后运行
INITIAL_PROMPT="请专注于修复所有 bug" ./run_dev_loop.sh 10
```

---

## 🔧 配置

### 方法 1: 直接编辑脚本

编辑 `run_dev_loop.sh`，找到配置部分：

```bash
# 修改初始 Prompt
INITIAL_PROMPT="请继续 SynergyAI 项目的开发工作..."

# 修改等待时间
WAIT_TIME_BETWEEN_ROUNDS=10
```

### 方法 2: 使用配置文件

```bash
# 1. 复制配置示例
cp dev_loop_config.example.sh dev_loop_config.sh

# 2. 编辑配置
vim dev_loop_config.sh

# 3. 在脚本中引入（修改 run_dev_loop.sh）
source "${PROJECT_DIR}/automation/dev_loop_config.sh"
```

---

## 📝 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `循环次数` | 必需，指定执行多少次开发循环 | `./run_dev_loop.sh 10` |

---

## 📈 进度监控

运行时会显示实时进度：

```
==================== 第 1/5 轮开发循环 ====================
[INFO] 检查服务器状态...
[STEP 1/3] 调用 Claude Code 执行开发任务...
[SUCCESS] 第 1 轮开发完成 (耗时: 5分18秒)
[STEP 2/3] 检查代码变更并提交...
[SUCCESS] 代码变更已提交
[SUCCESS] 代码已推送到远程仓库

进度: [20%] (1/5)
```

### 查看实时日志

在另一个终端：

```bash
# 实时查看主日志
tail -f logs/dev_loop_*.log
```

---

## 🎯 使用场景

| 场景 | 命令 | 说明 |
|------|------|------|
| **测试自动化** | `./run_dev_loop.sh 1` | 验证流程是否正常 |
| **连续开发** | `./run_dev_loop.sh 10` | AI 团队连续工作 |
| **过夜开发** | `nohup ./run_dev_loop.sh 50 &` | 让 AI 整夜工作 |
| **专项任务** | 修改 Prompt 后运行 | 专注于特定功能 |

---

## ⚠️ 使用前确认

### 1. Claude Code CLI 已安装

```bash
claude --version
```

如果未安装，访问：https://claude.ai/code

### 2. 开发环境正常

```bash
# 在项目根目录
python main.py
```

### 3. Git 配置正确

```bash
git remote -v
git config user.name
git config user.email
```

### 4. API 密钥已配置

确保 Claude Code 的 API 密钥已设置。

---

## 🛠️ 故障排除

### 问题 1: 服务器启动失败

**症状**: `服务器启动超时`

**解决**:
```bash
# 检查端口占用
netstat -ano | findstr :8000   # Windows
lsof -i :8000                 # Linux/macOS

# 终止占用进程
taskkill /F /PID <PID>         # Windows
kill -9 <PID>                 # Linux/macOS
```

### 问题 2: Claude Code 命令不存在

**症状**: `claude: command not found`

**解决**: 安装 Claude Code CLI，或修改脚本中的 `CLAUDE_CMD` 变量为完整路径。

### 问题 3: Git 推送失败

**症状**: `推送失败，请稍后手动推送`

**解决**:
```bash
# 检查远程仓库
git remote -v

# 手动推送测试
git push origin main
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART_AUTO.md](QUICKSTART_AUTO.md) | 30秒快速开始 |
| [AUTO_DEV_GUIDE.md](AUTO_DEV_GUIDE.md) | 完整使用指南 |
| [AUTO_DEV_SUMMARY.md](AUTO_DEV_SUMMARY.md) | 功能总结和配置说明 |

---

## 💡 最佳实践

1. **从小规模开始**: 先运行 1-2 轮，验证流程
2. **监控日志**: 实时查看日志，及时发现异常
3. **定期检查代码**: 运行结束后审查生成的代码质量
4. **优化 Prompt**: 根据效果调整初始 Prompt
5. **注意 API 配额**: 避免超出限制

---

## 🎯 工作流程

```
┌─────────────────────────────────────────┐
│  用户运行脚本                            │
│  ./run_dev_loop.sh 5                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  第 1 轮                                 │
│  ├─ 启动服务器                           │
│  ├─ 调用 Claude Code                     │
│  ├─ AI 团队完成任务                      │
│  ├─ 提交代码                             │
│  └─ 推送到 GitHub                        │
└────────────┬────────────────────────────┘
             │
             ▼
        [等待 5 秒]
             │
             ▼
┌─────────────────────────────────────────┐
│  第 2 轮...                              │
│  (重复上述流程)                          │
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  完成报告                                │
│  ├─ 总迭代次数: 5                        │
│  ├─ 成功次数: 5                          │
│  ├─ 总耗时: 25分18秒                     │
│  └─ 日志文件: logs/...                   │
└─────────────────────────────────────────┘
```

---

## 🎉 开始使用

```bash
# Windows 用户
cd automation
run_dev_loop.bat 5

# Linux/macOS 用户
cd automation
./run_dev_loop.sh 5
```

---

**SynergyAI** - 让 AI 团队协同工作 💪
