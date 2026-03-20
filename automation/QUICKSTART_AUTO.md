# 🚀 快速开始 - 自动化开发循环

## 📝 30 秒上手

### Windows 用户

```cmd
# 运行 5 次开发循环
run_dev_loop.bat 5
```

### Linux/macOS 用户

```bash
# 运行 5 次开发循环
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

---

## 📊 查看进度

运行时会看到：
```
==================== 第 1/5 轮开发循环 ====================
[INFO] 检查服务器状态...
[STEP 1/3] 调用 Claude Code 执行开发任务...
[SUCCESS] 第 1 轮开发完成
[STEP 2/3] 检查代码变更并提交...
[SUCCESS] 代码变更已提交
[SUCCESS] 代码已推送到远程仓库

进度: [20%] (1/5)
```

---

## 📁 查看日志

```bash
# 实时查看日志
tail -f logs/dev_loop_*.log
```

日志位置：`logs/` 目录

---

## 🛑 停止运行

**Windows**: `Ctrl + C`

**Linux/macOS**: `Ctrl + C`

---

## ⚙️ 高级用法

### 自定义 Prompt

编辑 `run_dev_loop.sh` (或 `.bat`)，找到这一行：

```bash
INITIAL_PROMPT="请继续 SynergyAI 项目的开发工作..."
```

改成你想要的内容：

```bash
INITIAL_PROMPT="请专注于开发用户认证模块，确保安全性测试通过。"
```

### 修改循环次数

```bash
# 执行 10 次
./run_dev_loop.sh 10

# 执行 50 次（过夜开发）
./run_dev_loop.sh 50
```

### 后台运行（Linux/macOS）

```bash
nohup ./run_dev_loop.sh 20 > logs/overnight.log 2>&1 &
```

---

## ⚠️ 注意事项

1. **确保 Claude Code CLI 已安装**
   ```bash
   # 检查安装
   claude --version
   ```

2. **确保开发环境正常**
   ```bash
   # 测试服务器
   python main.py
   ```

3. **确保 Git 配置正确**
   ```bash
   # 测试推送
   git push origin main
   ```

---

## 📚 详细文档

查看完整文档：[AUTO_DEV_GUIDE.md](AUTO_DEV_GUIDE.md)

---

## 🆘 遇到问题？

### 问题 1: `claude: command not found`

**解决**: 安装 Claude Code CLI
- 访问: https://claude.ai/code
- 下载并安装

### 问题 2: 服务器启动失败

**解决**: 手动测试
```bash
python main.py
```

### 问题 3: Git 推送失败

**解决**: 配置认证
```bash
git config --global credential.helper store
git push origin main
```

---

## 🎉 开始使用

```bash
# 第一次运行，测试 1 轮
./run_dev_loop.sh 1

# 如果成功，尝试更多轮
./run_dev_loop.sh 5
```

---

**SynergyAI** - 让 AI 团队协同工作 💪
