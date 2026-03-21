# ❓ 常见问题解答 (FAQ)

## 目录

- [安装和配置](#安装和配置)
- [使用和运行](#使用和运行)
- [性能和效率](#性能和效率)
- [故障和错误](#故障和错误)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)

---

## 安装和配置

### Q1: Claude Code CLI 是什么？从哪里下载？

**A**: Claude Code CLI 是 Anthropic 官方提供的命令行工具，可以让你在终端中直接使用 Claude AI。

**下载地址**: https://claude.ai/code

**安装步骤**:
1. 访问上述网址
2. 根据你的操作系统选择安装包
3. 安装完成后，运行 `claude --version` 验证

---

### Q2: 如何检查 Claude Code CLI 是否安装成功？

**A**:
```bash
# 在终端运行
claude --version

# 应显示版本号，例如:
# claude 0.5.0
```

如果显示 `command not found`，说明未安装或未添加到 PATH。

---

### Q3: 如何配置 Claude Code 的 API 密钥？

**A**: Claude Code CLI 会自动使用你的 Anthropic 账户配置。

1. 确保你已经注册了 Anthropic 账户
2. 登录 Claude Code CLI:
   ```bash
   claude login
   ```
3. 按照提示完成认证

---

### Q4: 需要什么版本的 Python？

**A**: 需要 Python 3.10 或更高版本。

**检查版本**:
```bash
python --version
# 或
python3 --version
```

如果版本过低，请升级 Python 或使用虚拟环境。

---

### Q5: 如何安装项目依赖？

**A**:
```bash
# 在项目根目录
pip install -r requirements.txt

# 或使用 pip3
pip3 install -r requirements.txt
```

---

### Q6: Git 配置需要注意什么？

**A**: 确保 Git 已正确配置用户信息和远程仓库：

```bash
# 检查用户名
git config user.name

# 检查邮箱
git config user.email

# 检查远程仓库
git remote -v

# 如果未配置，设置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 使用和运行

### Q7: 第一次运行应该执行几轮？

**A**: 建议第一次只运行 **1 轮**，用于验证环境配置。

```bash
# 第一次运行
./run_dev_loop.sh 1

# 查看日志，确认无误
cat logs/dev_loop_*.log

# 如果成功，可以增加轮数
./run_dev_loop.sh 5
```

---

### Q8: 脚本运行时间大概多久？

**A**: 每轮的时间取决于任务的复杂度：

- **简单任务**: 2-5 分钟
- **中等任务**: 5-10 分钟
- **复杂任务**: 10-20 分钟

例如，5 轮中等任务可能需要 25-50 分钟。

---

### Q9: 可以同时运行多个脚本实例吗？

**A**: **不推荐**。同时运行多个实例可能导致：

- 端口冲突（服务器启动失败）
- Git 提交冲突
- 日志混乱

建议一次只运行一个实例。

---

### Q10: 脚本会修改哪些文件？

**A**: 脚本主要会修改：

1. **项目代码文件**: 根据 feature_list.json 中的任务
2. **feature_list.json**: 更新任务状态
3. **Git 提交**: 自动创建 commit
4. **日志文件**: 在 `logs/` 目录

不会修改脚本文件本身或配置文件（除非明确指定）。

---

### Q11: 如何查看当前运行到第几轮？

**A**: 有三种方法：

**方法 1: 查看终端输出**
```
进度: [████████░░░░░░░░░░] 40% (2/5)
```

**方法 2: 查看日志**
```bash
grep "第.*轮" logs/dev_loop_*.log | tail -1
```

**方法 3: 查看日志文件数量**
```bash
ls -1 logs/claude_*.log | wc -l
```

---

### Q12: 可以中断脚本后继续运行吗？

**A**: 可以。脚本每次循环都是独立的，中断后可以继续运行。

**注意**: 继续运行时，AI 会从 feature_list.json 中读取当前状态，继续执行下一个待办任务。

---

## 性能和效率

### Q13: 如何提高脚本运行速度？

**A**: 有几个优化方向：

1. **减少等待时间**:
   ```bash
   # 编辑脚本，修改等待时间为 0
   WAIT_TIME_BETWEEN_ROUNDS=0
   ```

2. **使用更快的机器**: AI 运行速度受 CPU/内存影响

3. **优化 Prompt**: 更清晰的 Prompt 可以减少 AI 思考时间

4. **调整并发**: 修改 Claude Code 的并发参数（如果支持）

---

### Q14: 脚本会消耗多少 API 配额？

**A**: 取决于多个因素：

- **任务数量**: 每个任务都会调用 API
- **代码复杂度**: 复杂任务需要更多 token
- **测试运行**: 测试也会消耗 API

**估算**:
- 简单任务: ~5K-10K tokens
- 中等任务: ~10K-30K tokens
- 复杂任务: ~30K-100K tokens

建议监控 API 使用情况，避免超出配额。

---

### Q15: 可以限制脚本运行时间吗？

**A**: 可以使用系统的 `timeout` 命令：

**Linux/macOS**:
```bash
# 限制 1 小时
timeout 3600 ./run_dev_loop.sh 10

# 或使用后台任务 + cron 定时停止
```

**Windows**:
```cmd
REM 需要第三方工具或 PowerShell 脚本
```

---

## 故障和错误

### Q16: 脚本运行失败怎么办？

**A**: 按以下步骤排查：

1. **查看日志**
   ```bash
   cat logs/dev_loop_*.log
   ```

2. **检查错误信息**
   ```bash
   grep "\[ERROR\]" logs/dev_loop_*.log
   ```

3. **手动测试环境**
   ```bash
   # 测试服务器
   python main.py

   # 测试 Claude Code
   claude --version

   # 测试 Git
   git status
   ```

4. **查看故障排除指南**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

### Q17: 服务器启动失败怎么办？

**A**: 可能的原因和解决方案：

**原因 1: 端口被占用**
```bash
# 检查端口占用
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 终止占用进程
kill -9 <PID>  # Linux/macOS
taskkill /F /PID <PID>  # Windows
```

**原因 2: Python 环境问题**
```bash
# 检查 Python 版本
python --version

# 重新安装依赖
pip install -r requirements.txt
```

**原因 3: 代码错误**
```bash
# 手动运行服务器，查看错误信息
python main.py
```

---

### Q18: Git 提交或推送失败怎么办？

**A**: 常见原因和解决方案：

**原因 1: 认证失败**
```bash
# 重新配置认证
git config --global credential.helper store
git push origin main
# 按提示输入用户名和密码/PAT
```

**原因 2: 远程仓库不存在**
```bash
# 检查远程仓库
git remote -v

# 如果需要，添加远程仓库
git remote add origin https://github.com/username/repo.git
```

**原因 3: 冲突**
```bash
# 拉取最新代码
git pull origin main --rebase

# 如果有冲突，手动解决后
git add .
git rebase --continue
```

---

### Q19: AI 一直重复同一个任务怎么办？

**A**: 可能的原因：

1. **任务未正确标记为完成**
   - 检查 feature_list.json 中任务状态
   - 确认 AI 更新了任务状态

2. **feature_list.json 未提交**
   - 确认 Git 提交成功
   - 检查是否有冲突

3. **Prompt 不清晰**
   - 修改 INITIAL_PROMPT，明确要求更新任务状态

---

### Q20: 日志文件太大怎么办？

**A**: 日志管理建议：

1. **定期清理**
   ```bash
   # 删除 7 天前的日志
   find logs/ -name "*.log" -mtime +7 -delete
   ```

2. **压缩旧日志**
   ```bash
   # 压缩一个月前的日志
   find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
   ```

3. **配置日志轮转**: 可以修改脚本添加日志轮转功能

---

## 高级功能

### Q21: 如何自定义 AI 的开发任务？

**A**: 编辑 feature_list.json，添加或修改任务：

```json
{
  "id": "feat-021",
  "category": "feature",
  "priority": "high",
  "title": "你的任务标题",
  "description": "详细描述任务要求...",
  "status": "pending",
  "assignee_role": "dev",
  "steps": [
    "步骤 1",
    "步骤 2"
  ]
}
```

---

### Q22: 如何让 AI 专注于特定类型的任务？

**A**: 修改 INITIAL_PROMPT：

```bash
# 只修复 Bug
INITIAL_PROMPT="请只修复 Bug，不要开发新功能。优先级为 high > medium > low。"

# 只开发文档
INITIAL_PROMPT="请只完善文档，包括注释、README、API 文档等。"

# 只优化性能
INITIAL_PROMPT="请只做性能优化，不添加新功能。"
```

---

### Q23: 可以跳过某些任务吗？

**A**: 可以，在 feature_list.json 中将任务状态改为 "done" 或 "blocked"：

```json
{
  "id": "feat-007",
  "status": "done",  // 或 "blocked"
  "notes": "暂时跳过，以后再处理"
}
```

---

### Q24: 如何查看 AI 的开发历史？

**A**: 有几种方法：

1. **查看 Git 提交历史**
   ```bash
   git log --oneline --graph
   ```

2. **查看日志文件**
   ```bash
   cat logs/claude_*.log
   ```

3. **查看 feature_list.json**
   - 查看每个任务的 `updated_at` 时间戳
   - 查看任务的 `notes` 字段

---

### Q25: 可以在多个项目中使用这个脚本吗？

**A**: 可以，但需要修改脚本：

1. **复制脚本到目标项目**
2. **修改 PROJECT_DIR 变量**
3. **确保目标项目有 feature_list.json**
4. **确保 Claude Code 可以访问目标项目**

---

## 最佳实践

### Q26: 运行脚本前应该做什么准备？

**A**: 运行前检查清单：

- [ ] Claude Code CLI 已安装并登录
- [ ] Python 环境正常，依赖已安装
- [ ] Git 配置正确，可以推送
- [ ] 项目可以手动运行 (`python main.py`)
- [ ] feature_list.json 已准备
- [ ] 备份当前代码（可选）
- [ ] 确认有足够的 API 配额
- [ ] 确认有足够的磁盘空间（日志）

---

### Q27: 运行脚本后应该做什么？

**A**: 运行后检查清单：

- [ ] 查看日志，确认没有 ERROR
- [ ] 审查 Git 提交，检查代码质量
- [ ] 运行测试，确保功能正常
- [ ] 检查 feature_list.json 更新
- [ ] 更新项目文档（如果需要）
- [ ] 提交 Issue 报告问题（如果有）

---

### Q28: 如何监控脚本的运行状态？

**A**: 推荐方法：

1. **实时查看日志**
   ```bash
   tail -f logs/dev_loop_*.log
   ```

2. **定期检查 Git 提交**
   ```bash
   watch -n 10 "git log -1 --oneline"
   ```

3. **使用监控工具**（如 Prometheus + Grafana）

---

### Q29: 如何确保生成的代码质量？

**A**: 质量保证建议：

1. **审查每个提交**
   ```bash
   git diff HEAD~1
   ```

2. **运行测试套件**
   ```bash
   pytest
   ```

3. **代码静态分析**
   ```bash
   pylint core/
   flake8 core/
   ```

4. **手动测试关键功能**

---

### Q30: 什么时候适合使用这个自动化脚本？

**A**: 最佳使用场景：

✅ **适合**:
- 功能开发（CRUD、API、简单业务逻辑）
- Bug 修复（明确的问题描述）
- 测试编写（单元测试、集成测试）
- 文档完善（代码注释、API 文档）
- 重构任务（代码清理、模块化）

❌ **不适合**:
- 架构设计（需要人工决策）
- 复杂算法（需要仔细推敲）
- 性能调优（需要深入分析）
- 安全审计（需要专业判断）
- UI/UX 设计（需要创意和审美）

---

## 其他问题

### Q31: 脚本支持 Windows 吗？

**A**: 支持。使用 `run_dev_loop.bat` 批处理脚本。

注意：某些命令在 Windows 上可能需要调整。

---

### Q32: 如何报告 Bug 或建议新功能？

**A**: 请到项目 GitHub 仓库提交 Issue：

1. Bug 报告：包含错误日志、环境信息、复现步骤
2. 功能建议：详细描述需求和使用场景

---

### Q33: 有社区或论坛可以讨论吗？

**A**: 目前请通过 GitHub Issues 讨论。

未来可能会添加 Discord、Slack 等社区渠道。

---

### Q34: 脚本开源吗？可以二次开发吗？

**A**: 是的，脚本完全开源。

你可以：
- 修改脚本适应你的需求
- 提交 PR 改进脚本
- 分享你的经验

---

## 仍有问题？

如果以上 FAQ 没有解答你的问题：

1. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 查看 [AUTO_DEV_GUIDE.md](AUTO_DEV_GUIDE.md)
3. 查看日志文件: `logs/dev_loop_*.log`
4. 提交 Issue 到 GitHub 仓库

---

**SynergyAI** - 让 AI 团队协同工作 💪
