# 🔧 故障排除指南

## 目录

- [快速诊断](#快速诊断)
- [环境问题](#环境问题)
- [服务器问题](#服务器问题)
- [Claude Code 问题](#claude-code-问题)
- [Git 问题](#git-问题)
- [性能问题](#性能问题)
- [日志分析](#日志分析)
- [获取帮助](#获取帮助)

---

## 快速诊断

### 第一步：检查环境

运行以下命令，检查环境是否正常：

```bash
# 检查 Claude Code CLI
claude --version

# 检查 Python
python --version

# 检查项目依赖
pip list | grep fastapi

# 检查 Git
git status
git remote -v

# 检查项目运行
python main.py &
# 访问 http://localhost:8000/docs
```

**如果所有检查都通过，跳转到对应的问题章节。**

---

## 环境问题

### 问题 1: Claude Code CLI 未安装

**症状**:
```bash
$ claude --version
bash: claude: command not found
```

**解决方案**:

1. **安装 Claude Code CLI**
   - 访问: https://claude.ai/code
   - 下载适合你操作系统的安装包
   - 按照官方文档安装

2. **验证安装**
   ```bash
   claude --version
   # 应显示版本号
   ```

3. **如果仍然找不到命令**
   - 检查 PATH 环境变量
   - 重启终端
   - 使用完整路径调用 Claude Code

---

### 问题 2: Python 版本过低

**症状**:
```bash
$ python --version
Python 3.8.5
# 需要 3.10+
```

**解决方案**:

**方法 1: 升级 Python**
```bash
# macOS (使用 Homebrew)
brew upgrade python

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Windows
# 从 python.org 下载最新版本
```

**方法 2: 使用 pyenv**
```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 安装 Python 3.11
pyenv install 3.11.0

# 设置本地 Python 版本
pyenv local 3.11.0
```

**方法 3: 使用虚拟环境**
```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

---

### 问题 3: 依赖安装失败

**症状**:
```bash
$ pip install -r requirements.txt
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案**:

1. **升级 pip**
   ```bash
   pip install --upgrade pip
   ```

2. **使用国内镜像源**
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **逐个安装依赖**
   ```bash
   # 查看哪个包失败
   pip install fastapi
   pip install uvicorn
   # ...
   ```

4. **检查 Python 版本兼容性**
   ```bash
   # 某些包可能不支持你的 Python 版本
   python --version
   ```

---

### 问题 4: Git 未配置

**症状**:
```bash
$ git commit
*** Please tell me who you are.
```

**解决方案**:

```bash
# 配置用户名
git config --global user.name "Your Name"

# 配置邮箱
git config --global user.email "your.email@example.com"

# 验证配置
git config --list | grep user
```

---

## 服务器问题

### 问题 5: 服务器启动失败

**症状**:
```
[ERROR] 服务器启动超时
```

**诊断步骤**:

1. **手动启动服务器**
   ```bash
   cd /path/to/project
   python main.py
   ```

2. **查看错误信息**
   - 服务器会输出详细的错误日志
   - 根据错误信息修复问题

**常见原因和解决方案**:

**原因 1: 端口被占用**
```bash
# 检查端口占用
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 终止占用进程
kill -9 <PID>  # Linux/macOS
taskkill /F /PID <PID>  # Windows
```

**原因 2: 依赖缺失**
```bash
# 重新安装依赖
pip install -r requirements.txt
```

**原因 3: 代码错误**
```bash
# 查看详细错误
python main.py --debug

# 修复代码错误
```

**原因 4: 权限问题**
```bash
# Linux/macOS
chmod +x main.py

# 检查文件权限
ls -l main.py
```

---

### 问题 6: 服务器频繁重启

**症状**:
```
[WARNING] 检测到服务器崩溃，正在重启...
```

**解决方案**:

1. **查看服务器日志**
   ```bash
   cat logs/server_*.log
   ```

2. **检查内存使用**
   ```bash
   # Linux/macOS
   free -h
   top

   # Windows
   taskmgr
   ```

3. **检查代码是否有无限循环**
   ```bash
   # 使用代码审查工具
   pylint core/
   ```

4. **增加服务器重启超时时间**
   ```bash
   # 编辑脚本，修改 SERVER_TIMEOUT
   local server_timeout=30  # 增加到 30 秒
   ```

---

### 问题 7: 服务器响应慢

**症状**:
- API 响应时间 > 5 秒
- 页面加载缓慢

**解决方案**:

1. **检查系统资源**
   ```bash
   # CPU
   top

   # 内存
   free -h

   # 磁盘 I/O
   iotop
   ```

2. **检查数据库性能**
   ```bash
   # 如果使用数据库
   # 检查慢查询日志
   ```

3. **优化代码**
   - 添加缓存
   - 优化数据库查询
   - 使用异步处理

4. **增加服务器资源**
   - 升级硬件
   - 使用更快的机器

---

## Claude Code 问题

### 问题 8: Claude Code 无响应

**症状**:
```
[STEP 1/3] 调用 Claude Code 执行开发任务...
(长时间无输出)
```

**解决方案**:

1. **检查网络连接**
   ```bash
   ping api.anthropic.com
   ```

2. **检查 API 密钥**
   ```bash
   claude login
   ```

3. **查看 Claude 日志**
   ```bash
   cat logs/claude_*.log
   ```

4. **增加超时时间**
   ```bash
   # 编辑脚本，修改 CLAUDE_TIMEOUT
   local claude_timeout=3600  # 增加到 1 小时
   ```

5. **检查 API 配额**
   - 登录 Anthropic 控制台
   - 查看 API 使用情况

---

### 问题 9: Claude Code 权限被拒绝

**症状**:
```
[ERROR] Claude Code 执行失败: Permission denied
```

**解决方案**:

1. **检查脚本参数**
   ```bash
   # 确保 --allow-permissions 参数存在
   grep "allow-permissions" run_dev_loop.sh
   ```

2. **手动测试权限**
   ```bash
   claude --yes --no-interactive --allow-permissions "test"
   ```

3. **检查文件权限**
   ```bash
   # Linux/macOS
   ls -l core/
   chmod -R +w core/

   # Windows
   # 右键文件夹 -> 属性 -> 安全
   ```

4. **使用 sudo（不推荐）**
   ```bash
   sudo ./run_dev_loop.sh 1
   ```

---

### 问题 10: Claude Code 输出乱码

**症状**:
- Claude 输出包含乱码字符
- 中文显示不正常

**解决方案**:

1. **设置终端编码**
   ```bash
   # Linux/macOS
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8

   # Windows PowerShell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```

2. **检查 Python 编码**
   ```python
   # 在 main.py 开头添加
   # -*- coding: utf-8 -*-
   ```

---

## Git 问题

### 问题 11: Git 推送失败

**症状**:
```
[ERROR] 推送失败，请稍后手动推送
```

**诊断步骤**:

1. **手动推送测试**
   ```bash
   git push origin main
   ```

2. **查看错误信息**
   - Git 会输出详细的失败原因

**常见原因和解决方案**:

**原因 1: 认证失败**
```bash
# 配置凭证助手
git config --global credential.helper store

# 重新推送
git push origin main
# 输入用户名和密码/PAT
```

**原因 2: 远程仓库不存在**
```bash
# 检查远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/username/repo.git
```

**原因 3: 分支不匹配**
```bash
# 检查当前分支
git branch

# 推送到正确分支
git push origin $(git branch --show-current)
```

**原因 4: 网络问题**
```bash
# 检查网络连接
ping github.com

# 使用 SSH 替代 HTTPS
git remote set-url origin git@github.com:username/repo.git
```

---

### 问题 12: Git 提交失败

**症状**:
```
[ERROR] 代码提交失败
```

**解决方案**:

1. **检查 Git 状态**
   ```bash
   git status
   ```

2. **检查是否有未解决的合并冲突**
   ```bash
   git diff --check
   ```

3. **手动提交测试**
   ```bash
   git add .
   git commit -m "test commit"
   ```

4. **检查 Git 配置**
   ```bash
   git config --list
   ```

---

### 问题 13: Git 冲突

**症状**:
```
CONFLICT (content): Merge conflict in file.py
```

**解决方案**:

1. **查看冲突文件**
   ```bash
   git status
   ```

2. **手动解决冲突**
   ```bash
   # 编辑冲突文件，标记如下:
   # <<<<<<< HEAD
   # 你的代码
   # =======
   # 别人的代码
   # >>>>>>> main
   ```

3. **标记冲突已解决**
   ```bash
   git add <resolved_file>
   ```

4. **继续合并**
   ```bash
   git commit
   ```

---

## 性能问题

### 问题 14: 脚本运行缓慢

**症状**:
- 每轮耗时 > 20 分钟
- AI 响应慢

**解决方案**:

1. **优化 Prompt**
   ```bash
   # 使用更简洁明确的 Prompt
   INITIAL_PROMPT="修复 feat-001，快速测试，提交代码。"
   ```

2. **减少等待时间**
   ```bash
   WAIT_TIME_BETWEEN_ROUNDS=0
   ```

3. **使用更快的机器**
   - 升级 CPU
   - 增加内存
   - 使用 SSD

4. **优化代码**
   - 减少 AI 的工作量
   - 分解大任务为小任务

---

### 问题 15: 内存占用过高

**症状**:
```
[ERROR] 内存不足
```

**解决方案**:

1. **检查内存使用**
   ```bash
   # Linux/macOS
   free -h
   top

   # Windows
   taskmgr
   ```

2. **限制内存使用**
   ```bash
   # 限制 Python 内存
   ulimit -v 4194304  # 4GB
   ```

3. **清理日志**
   ```bash
   # 删除旧日志
   find logs/ -name "*.log" -mtime +7 -delete
   ```

4. **重启脚本**
   ```bash
   # 定期重启脚本释放内存
   ```

---

## 日志分析

### 如何查看日志

1. **主日志**
   ```bash
   cat logs/dev_loop_*.log
   ```

2. **服务器日志**
   ```bash
   cat logs/server_*.log
   ```

3. **Claude 日志**
   ```bash
   cat logs/claude_*.log
   ```

4. **实时查看**
   ```bash
   tail -f logs/dev_loop_*.log
   ```

### 常见日志模式

**正常流程**:
```
[INFO] ==================== 第 1/5 轮开发循环 ====================
[INFO] 检查服务器状态...
[STEP 1/3] 调用 Claude Code 执行开发任务...
[SUCCESS] 第 1 轮开发完成
[STEP 2/3] 检查代码变更并提交...
[SUCCESS] 代码变更已提交
[SUCCESS] 代码已推送到远程仓库
```

**异常流程**:
```
[ERROR] 服务器启动超时
[ERROR] Claude Code 执行失败
[ERROR] 推送失败，请稍后手动推送
```

### 日志级别说明

- `[INFO]` - 一般信息
- `[SUCCESS]` - 成功操作
- `[WARNING]` - 警告信息
- `[ERROR]` - 错误信息（需要关注）
- `[STEP n/m]` - 进度步骤

---

## 获取帮助

### 自助诊断清单

运行以下命令，收集诊断信息：

```bash
# 系统信息
uname -a  # Linux/macOS
systeminfo  # Windows

# Python 信息
python --version
pip list

# Git 信息
git --version
git remote -v

# Claude Code 信息
claude --version

# 日志信息
ls -lh logs/

# 错误信息
grep "\[ERROR\]" logs/dev_loop_*.log | tail -20
```

### 提交 Issue

如果以上方法都无法解决问题，请提交 Issue：

1. **标题**: 简明描述问题
   - 例如: "服务器启动失败 - 端口占用"

2. **内容**: 包含以下信息
   - 操作系统和版本
   - Python 版本
   - Claude Code 版本
   - 错误日志
   - 复现步骤
   - 已尝试的解决方法

3. **附件**:
   - 相关日志文件
   - 错误截图

### 联系方式

- GitHub Issues: [项目仓库]/issues
- Email: [项目维护者邮箱]

---

## 预防措施

### 定期检查

```bash
# 每周检查一次
# 1. 清理日志
find logs/ -name "*.log" -mtime +7 -delete

# 2. 检查磁盘空间
df -h

# 3. 检查 API 配额
# 登录 Anthropic 控制台

# 4. 备份代码
git push origin main
```

### 监控建议

1. **设置日志监控**
   ```bash
   # 监控错误日志
   tail -f logs/dev_loop_*.log | grep "\[ERROR\]"
   ```

2. **设置告警**
   - 使用监控工具（如 Prometheus）
   - 配置邮件/Slack 通知

3. **定期审查**
   - 每周审查 AI 生成的代码
   - 检查 Git 提交历史
   - 更新 feature_list.json

---

**SynergyAI** - 让 AI 团队协同工作 💪
