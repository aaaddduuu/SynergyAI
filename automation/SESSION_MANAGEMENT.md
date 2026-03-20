# 🔁 会话管理与 /clear 处理机制

## 问题描述

在使用 Claude Code 进行长时间自动化开发时，会遇到以下问题：

1. **Token 限制** - 对话过长时超过上下文窗口限制
2. **性能下降** - 累积的上下文导致响应变慢
3. **内存溢出** - 长对话会消耗大量内存
4. **手动清理** - 需要输入 `/clear` 命令清除会话

## 解决方案

### 1. 会话隔离机制

每个任务都使用**完全独立的新会话**：

```python
# 为每次任务生成新的会话 ID
import uuid
session_id = str(uuid.uuid4())

cmd = [
    "claude",
    "-p",  # print 模式
    "--permission-mode", "dontAsk",
    "--no-session-persistence",  # ← 禁用会话持久化
    "--session-id", session_id,  # ← 使用新的会话 ID
    project_dir
]
```

**效果**：
- ✅ 每个任务完全独立
- ✅ 不会累积上下文
- ✅ 避免 token 限制
- ✅ 自动处理，无需手动 /clear

### 2. 错误检测机制

自动检测和处理 token 限制相关错误：

```python
error_indicators = [
    "token", "too long", "maximum",
    "limit", "context", "memory", "/clear"
]

combined_output = (stdout + stderr).lower()
has_error = any(indicator in combined_output for indicator in error_indicators)

if has_error:
    log("警告: 检测到会话长度或 token 限制")
    log("下次任务会使用新会话")
```

**检测的错误类型**：
- Token 限制错误
- 上下文过长错误
- 内存限制错误
- 其他会话相关错误

### 3. 会话生命周期

```
任务 N 开始
  ├─ 生成新的 UUID 会话 ID
  ├─ 设置 --no-session-persistence
  ├─ 调用 Claude Code（全新会话）
  ├─ 执行任务
  └─ 会话结束（不保存）

任务 N+1 开始
  ├─ 生成另一个新的 UUID 会话 ID
  ├─ 再次使用 --no-session-persistence
  ├─ 调用 Claude Code（全新会话）
  └─ ...
```

**关键特性**：
- 每个会话只用于一个任务
- 会话之间完全隔离
- 不会保存到磁盘
- 自动清理

## 技术细节

### Claude Code CLI 参数

| 参数 | 作用 |
|------|------|
| `-p` | Print 模式，非交互式 |
| `--no-session-persistence` | 禁用会话持久化，不保存到磁盘 |
| `--session-id <uuid>` | 指定会话 ID |
| `--permission-mode dontAsk` | 不询问权限 |

### 为什么有效

1. **无状态设计**
   - 每次调用都是独立的
   - 不依赖之前的对话历史
   - 每个任务的 prompt 都是完整的

2. **Token 优化**
   - 每个会话只处理一个任务
   - 上下文窗口始终是新的
   - 避免 token 累积

3. **自动清理**
   - 会话不保存到磁盘
   - 内存自动释放
   - 无需手动清理

## 实际效果

### Before (有问题)
```
任务 1: [会话 A]
任务 2: [会话 A + 任务1上下文] ← 开始累积
任务 3: [会话 A + 任务1+2上下文] ← 越来越长
任务 4: [会话 A + 任务1+2+3上下文] ← Token 限制！
需要手动 /clear
```

### After (已修复)
```
任务 1: [全新会话 A] ✅
任务 2: [全新会话 B] ✅ (独立)
任务 3: [全新会话 C] ✅ (独立)
任务 4: [全新会话 D] ✅ (独立)
无需手动操作
```

## 验证方法

### 查看日志
```
[2026-03-21 01:25:10] 会话 ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
[2026-03-21 01:29:13] 会话 ID: b2c3d4e5-f6a7-8901-bcde-f12345678901
[2026-03-21 01:33:45] 会话 ID: c3d4e5f6-a7b8-9012-cdef-123456789012
```

每个任务都有不同的会话 ID！

### 检查进程
```bash
# 不会有长时间运行的 Claude Code 进程
ps aux | grep claude
```

### 内存使用
```bash
# 内存使用保持稳定
# 不会因为会话累积而增长
```

## 优点

✅ **自动化** - 无需手动输入 /clear
✅ **稳定性** - 避免 token 限制
✅ **性能** - 每次都是干净的上下文
✅ **可扩展** - 可以运行任意数量的任务
✅ **隔离性** - 任务之间互不影响

## 注意事项

### Prompt 设计

由于每个任务都是新会话，prompt 必须是**自包含的**：

```python
# ✅ 好的 prompt - 包含所有上下文
prompt = f"""请完成以下任务：

【项目背景】SynergyAI 是一个多智能体协作系统...
【任务描述】{feature.description}
【任务步骤】
1. ...
2. ...
3. ...

请遵循以下原则：
- 使用 Python 3.9+
- 遵循 SOLID 原则
- ... (所有规则都列出来)
"""

# ❌ 差的 prompt - 假设有上下文
prompt = "继续上一个任务..."  # 新会话不知道上一个任务
```

### 代价

- 每个 prompt 都需要包含完整的上下文
- 稍微增加了一些 token 使用（但远低于累积的代价）
- 无法引用之前的对话（但这是设计目标）

## 监控和维护

### 日志监控

关注日志中的以下信息：

```
# 正常情况
[INFO] 会话 ID: xxx-xxx-xxx
[INFO] Claude Code 执行成功

# 需要注意
[WARNING] 检测到会话长度或 token 限制相关错误
[WARNING] 这通常不影响执行
```

### 性能指标

```python
# 可以添加到自动化脚本
import psutil
import time

start_time = time.time()
start_memory = psutil.virtual_memory().used

# 执行任务
run_claude_code(prompt)

# 计算资源使用
elapsed = time.time() - start_time
memory_used = psutil.virtual_memory().used - start_memory
```

## 未来改进

可能的优化方向：

1. **智能上下文管理**
   - 检测任务相关性
   - 相关任务共享部分上下文
   - 无关任务完全隔离

2. **会话池**
   - 预创建多个会话
   - 复用空闲会话
   - 动态扩缩容

3. **Prompt 优化**
   - 压缩上下文信息
   - 使用更简洁的描述
   - 动态调整 prompt 长度

4. **错误恢复**
   - 检测到 token 错误自动重试
   - 使用简化的 prompt 重试
   - 降级策略

## 总结

通过使用**会话隔离**机制，我们完全解决了长时间运行时的 token 限制问题：

- ✅ 每个任务独立运行
- ✅ 自动清理上下文
- ✅ 无需手动 /clear
- ✅ 可以无限运行

这使得自动化开发系统可以**7x24小时稳定运行**，完成大量任务！🚀
