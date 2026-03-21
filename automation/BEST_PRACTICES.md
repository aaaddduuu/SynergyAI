# 📋 最佳实践指南

## 目录

- [快速入门最佳实践](#快速入门最佳实践)
- [任务管理最佳实践](#任务管理最佳实践)
- [Prompt 工程最佳实践](#prompt-工程最佳实践)
- [代码质量最佳实践](#代码质量最佳实践)
- [性能优化最佳实践](#性能优化最佳实践)
- [安全最佳实践](#安全最佳实践)
- [团队协作最佳实践](#团队协作最佳实践)
- [监控和维护最佳实践](#监控和维护最佳实践)

---

## 快速入门最佳实践

### 1. 渐进式启动策略

❌ **错误做法**:
```bash
# 直接运行 100 轮
./run_dev_loop.sh 100
```

✅ **正确做法**:
```bash
# 第 1 步: 测试 1 轮
./run_dev_loop.sh 1

# 第 2 步: 检查日志
cat logs/dev_loop_*.log

# 第 3 步: 审查代码
git diff HEAD~1

# 第 4 步: 确认无误后运行 5 轮
./run_dev_loop.sh 5

# 第 5 步: 再次检查
# ...

# 第 6 步: 最后规模化运行
./run_dev_loop.sh 50
```

**理由**: 渐进式启动可以及早发现问题，避免大规模错误。

---

### 2. 环境验证清单

运行脚本前，务必验证：

```bash
# 1. Claude Code CLI
claude --version

# 2. Python 环境
python --version
pip list | grep fastapi

# 3. Git 配置
git config user.name
git config user.email
git remote -v

# 4. 项目运行
python main.py &
# 访问 http://localhost:8000/docs

# 5. API 配额
# 登录 Anthropic 控制台检查
```

---

### 3. 备份策略

```bash
# 运行前创建备份
git checkout -b backup-$(date +%Y%m%d)
git push origin backup-$(date +%Y%m%d)

# 或者创建代码快照
cp -r . ../synergyai-backup-$(date +%Y%m%d)
```

---

## 任务管理最佳实践

### 4. 任务优先级设计

**高优先级任务**:
- 阻塞性 Bug
- 安全漏洞
- 核心功能缺失

**中优先级任务**:
- 新功能开发
- 性能优化
- 测试覆盖

**低优先级任务**:
- 代码重构
- 文档完善
- UI 优化

**feature_list.json 示例**:
```json
{
  "id": "feat-001",
  "priority": "high",
  "title": "修复登录 Bug",
  "description": "用户无法登录，需要立即修复",
  "status": "pending"
},
{
  "id": "feat-002",
  "priority": "medium",
  "title": "添加用户头像功能",
  "description": "允许用户上传头像",
  "status": "pending"
},
{
  "id": "feat-003",
  "priority": "low",
  "title": "优化界面配色",
  "description": "改进 UI 颜色方案",
  "status": "pending"
}
```

---

### 5. 任务粒度控制

❌ **任务过大**:
```json
{
  "title": "实现完整的电商系统",
  "description": "包括用户管理、商品管理、订单、支付..."
}
```

✅ **任务拆分**:
```json
{
  "title": "实现用户注册功能",
  "description": "用户可以通过邮箱注册账号",
  "steps": [
    "创建注册 API",
    "实现邮箱验证",
    "添加注册表单",
    "测试注册流程"
  ]
}
```

**建议**: 每个任务应该可以在 5-15 分钟内完成。

---

### 6. 任务依赖管理

使用 `notes` 字段标注依赖关系：

```json
{
  "id": "feat-005",
  "title": "实现订单功能",
  "status": "pending",
  "notes": "依赖 feat-003 (商品管理) 和 feat-004 (购物车)"
}
```

或者使用 `blocked` 状态：

```json
{
  "id": "feat-005",
  "title": "实现订单功能",
  "status": "blocked",
  "notes": "等待商品管理功能完成"
}
```

---

### 7. 角色分配策略

**dev (开发者)**: 代码实现、Bug 修复
```json
{
  "assignee_role": "dev",
  "title": "实现用户注册 API"
}
```

**architect (架构师)**: 架构设计、技术选型
```json
{
  "assignee_role": "architect",
  "title": "设计数据库架构"
}
```

**qa (测试工程师)**: 测试编写、质量保证
```json
{
  "assignee_role": "qa",
  "title": "编写集成测试"
}
```

**ba (业务分析师)**: 需求分析、文档完善
```json
{
  "assignee_role": "ba",
  "title": "编写 API 文档"
}
```

---

## Prompt 工程最佳实践

### 8. 清晰明确的 Prompt

❌ **模糊 Prompt**:
```bash
INITIAL_PROMPT="继续开发"
```

✅ **明确 Prompt**:
```bash
INITIAL_PROMPT="请继续 SynergyAI 项目的开发工作。请遵循以下原则：
1. 一次只处理一个任务
2. 每个任务完成后更新 feature_list.json
3. 运行测试确保功能正常
4. 提交代码时使用清晰的 commit message
5. 优先处理 high 优先级的任务"
```

---

### 9. 上下文感知 Prompt

根据当前项目状态调整 Prompt：

```bash
# 项目初期：功能开发
INITIAL_PROMPT="专注于核心功能开发，确保基础架构稳定。"

# 项目中期：功能完善
INITIAL_PROMPT="完善现有功能，添加测试，提高代码质量。"

# 项目后期：优化和文档
INITIAL_PROMPT="优化性能，完善文档，准备发布。"
```

---

### 10. 约束条件 Prompt

添加必要的约束：

```bash
INITIAL_PROMPT="请继续开发项目。请注意：
1. 所有代码必须遵循项目规范
2. 每个函数必须有文档字符串
3. 测试覆盖率不能低于 70%
4. 不允许引入新的依赖（除非必要）
5. 所有 API 必须有错误处理"
```

---

### 11. 迭代优化 Prompt

根据 AI 的表现调整 Prompt：

```bash
# 第 1 版 Prompt
INITIAL_PROMPT="开发用户认证功能"

# 观察到 AI 忘记测试，改进为：
INITIAL_PROMPT="开发用户认证功能，必须包含单元测试和集成测试"

# 观察到 AI 测试不充分，再次改进为：
INITIAL_PROMPT="开发用户认证功能。
1. 实现注册、登录、注销 API
2. 编写至少 5 个单元测试
3. 编写 3 个集成测试
4. 确保测试覆盖率达到 80% 以上
5. 运行 pytest --cov 检查覆盖率"
```

---

## 代码质量最佳实践

### 12. 代码审查流程

每轮运行后，务必审查代码：

```bash
# 1. 查看最近的提交
git log -5 --oneline

# 2. 查看代码变更
git diff HEAD~3

# 3. 检查特定文件
git diff HEAD~1 -- core/agents.py

# 4. 查看提交详情
git show <commit-hash>
```

---

### 13. 自动化测试

确保 AI 生成的代码包含测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agents.py

# 检查测试覆盖率
pytest --cov=core --cov-report=html
```

**Prompt 示例**:
```bash
INITIAL_PROMPT="开发功能时，必须同时编写测试：
1. 单元测试：测试单个函数
2. 集成测试：测试模块协作
3. 运行 pytest 确保通过
4. 测试覆盖率不低于 70%"
```

---

### 14. 代码规范

在 Prompt 中强调代码规范：

```bash
INITIAL_PROMPT="编写代码时，请遵循：
1. PEP 8 代码风格
2. 类型注解（Type Hints）
3. 文档字符串（Docstrings）
4. 有意义的变量命名
5. 单一职责原则
6. DRY（Don't Repeat Yourself）"
```

---

### 15. 静态分析

定期运行静态分析工具：

```bash
# pylint: 代码质量检查
pylint core/

# flake8: 代码风格检查
flake8 core/

# mypy: 类型检查
mypy core/

# black: 代码格式化
black core/
```

---

## 性能优化最佳实践

### 16. 资源监控

监控脚本运行时的资源使用：

```bash
# CPU 和内存
top

# 磁盘 I/O
iotop

# 网络连接
netstat -tuln
```

---

### 17. 日志管理

定期清理和压缩日志：

```bash
# 删除 7 天前的日志
find logs/ -name "*.log" -mtime +7 -delete

# 压缩 30 天前的日志
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;

# 设置日志轮转
# 在脚本中添加：
# 自动删除超过 100MB 的日志
```

---

### 18. 并发控制

避免同时运行多个实例：

```bash
# 检查是否有实例在运行
pgrep -f run_dev_loop.sh

# 如果有，先停止
pkill -f run_dev_loop.sh

# 然后启动新实例
./run_dev_loop.sh 5
```

---

### 19. API 配额管理

监控 API 使用情况：

```bash
# 在日志中记录 token 使用
# 查看最近的 API 调用
grep "tokens" logs/claude_*.log | tail -20

# 设置每日限额
# 在 Prompt 中提醒 AI：
INITIAL_PROMPT="注意控制 token 使用，单次任务不超过 50K tokens"
```

---

## 安全最佳实践

### 20. 敏感信息保护

**不要**在 feature_list.json 或 Prompt 中包含：
- API 密钥
- 密码
- 访问令牌
- 私有密钥

✅ **正确做法**:
```bash
# 使用环境变量
export API_KEY="your-secret-key"

# 在代码中引用
api_key = os.getenv("API_KEY")
```

---

### 21. Git 安全配置

```bash
# 启用 GPG 签名
git config --global commit.gpgsign true

# 配置 .gitignore
echo "*.key
*.pem
.env
secret.json" >> .gitignore
```

---

### 22. 权限控制

谨慎使用 `--allow-permissions`：

```bash
# 开发环境：允许所有权限
claude --yes --no-interactive --allow-permissions "test"

# 生产环境：限制权限
claude --yes --no-interactive "test"
# 只在必要时手动确认
```

---

## 团队协作最佳实践

### 23. 分支策略

使用功能分支隔离开发：

```bash
# 创建功能分支
git checkout -b feat/automation

# 运行自动化脚本
./run_dev_loop.sh 10

# 完成后合并
git checkout main
git merge feat/automation
```

---

### 24. 代码审查流程

1. **AI 生成代码**
2. **人工审查**
   ```bash
   git diff HEAD~1
   ```

3. **测试验证**
   ```bash
   pytest
   ```

4. **批准合并**
   ```bash
   git log -1 --pretty=format:"%H %s" > approval.txt
   ```

---

### 25. 文档同步

确保文档与代码同步：

```bash
# 在任务列表中添加文档任务
{
  "id": "feat-100",
  "title": "更新 API 文档",
  "description": "同步更新 API 文档，反映最新变更",
  "status": "pending"
}
```

---

## 监控和维护最佳实践

### 26. 实时监控

使用监控工具跟踪进度：

```bash
# 监控脚本输出
tail -f logs/dev_loop_*.log

# 监控错误
tail -f logs/dev_loop_*.log | grep ERROR

# 监控 Git 提交
watch -n 10 "git log -1 --oneline"
```

---

### 27. 定期报告

生成定期开发报告：

```bash
# 每日报告
git log --since="1 day ago" --pretty=format:"%h %s" > daily_report.txt

# 统计完成数量
grep "done" feature_list.json | wc -l

# 统计代码行数
git diff --stat HEAD~10
```

---

### 28. 健康检查

定期执行健康检查：

```bash
# 1. 检查服务器状态
curl http://localhost:8000/health

# 2. 检查测试通过率
pytest --tb=no -q

# 3. 检查代码覆盖率
pytest --cov=core --cov-report=term-missing

# 4. 检查日志中的错误
grep ERROR logs/dev_loop_*.log | wc -l
```

---

### 29. 备份和恢复

定期备份重要数据：

```bash
# 备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
git archive --format=tar.gz --output=../backup-$DATE.tar.gz HEAD
cp feature_list.json ../feature_list-$DATE.json.bak
```

---

### 30. 持续改进

收集反馈，持续优化：

1. **记录问题**: 在 feature_list.json 的 `notes` 字段
2. **分析日志**: 定期查看错误日志
3. **优化 Prompt**: 根据 AI 表现调整
4. **更新文档**: 保持文档与实际使用一致

---

## 总结

### 核心原则

1. **渐进式启动**: 从小规模开始，逐步扩大
2. **持续审查**: 定期检查代码质量
3. **明确约束**: 在 Prompt 中设置清晰规则
4. **监控日志**: 实时跟踪 AI 工作状态
5. **安全第一**: 保护敏感信息，控制权限
6. **团队协作**: 建立代码审查流程
7. **持续改进**: 根据反馈优化系统

### 快速检查清单

运行脚本前：
- [ ] 环境验证完成
- [ ] 代码已备份
- [ ] 任务清单已准备
- [ ] Prompt 已优化
- [ ] 监控工具已准备

运行脚本后：
- [ ] 日志已检查
- [ ] 代码已审查
- [ ] 测试已通过
- [ ] 文档已更新
- [ ] 备份已创建

---

**SynergyAI** - 让 AI 团队协同工作 💪
