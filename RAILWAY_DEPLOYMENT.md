# 🚀 SynergyAI - Railway 部署指南

本文档介绍如何将 SynergyAI 部署到 Railway 平台。

---

## 📋 前置要求

- GitHub 仓库（已完成：https://github.com/aaaddduuu/SynergyAI）
- Railway 账号（https://railway.app/）

---

## 🚀 部署步骤

### 方法一：通过 Railway 控制台部署（推荐）

#### 1. 登录 Railway

访问 https://railway.app/ 并登录（支持 GitHub 登录）

#### 2. 创建新项目

- 点击 **"New Project"**
- 选择 **"Deploy from GitHub repo"**

#### 3. 连接 GitHub 仓库

- 搜索并选择 `SynergyAI` 仓库
- 点击 **"Import"**

#### 4. 配置环境变量

Railway 会自动检测 Python 项目并安装依赖。接下来需要配置环境变量：

在项目设置 → **Variables** 中添加以下变量：

```bash
# 必需配置
PYTHONUNBUFFERED=1
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secure_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# 可选：数据库配置（默认使用 SQLite）
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# 可选：API 配置
# OPENAI_API_KEY=your_openai_api_key
# OPENAI_BASE_URL=https://api.openai.com/v1

# CORS 配置（重要！需要添加 Railway 域名）
CORS_ORIGINS=https://your-app.railway.app,http://localhost:8000
```

**生成密钥的方法：**
```bash
# 使用 Python 生成
python -c "import secrets; print(secrets.token_hex(32))"

# 或使用 OpenSSL
openssl rand -hex 32
```

#### 5. 部署

- 点击 **"Deploy"** 按钮
- 等待部署完成（通常需要 2-3 分钟）
- Railway 会自动：
  - 安装 Python 依赖
  - 启动 FastAPI 服务器
  - 分配 HTTPS 域名

#### 6. 获取访问地址

部署成功后，Railway 会提供一个域名：
```
https://your-app-name.railway.app
```

---

### 方法二：通过 Railway CLI 部署

#### 1. 安装 Railway CLI

```bash
npm install -g railway
```

#### 2. 登录

```bash
railway login
```

#### 3. 初始化项目

```bash
cd D:\Androdi-Project\ai-github-project\ai-coworker
railway init
```

#### 4. 配置环境变量

```bash
railway variables set PYTHONUNBUFFERED=1
railway variables set API_HOST=0.0.0.0
railway variables set API_PORT=8000
railway variables set SECRET_KEY=your_secret_key
railway variables set JWT_SECRET_KEY=your_jwt_secret
```

#### 5. 部署

```bash
railway up
```

#### 6. 查看日志

```bash
railway logs
```

#### 7. 打开部署的应用

```bash
railway open
```

---

## 🔧 部署后配置

### 1. 更新 CORS 配置

部署成功后，需要将 Railway 分配的域名添加到 CORS 白名单：

```bash
# 在 Railway Variables 中更新
CORS_ORIGINS=https://your-app-name.railway.app,http://localhost:8000
```

### 2. 验证部署

访问 `https://your-app-name.railway.app`，应该能看到 SynergyAI 界面。

### 3. 配置 AI 模型

在应用界面中：
1. 点击 **Settings** 按钮
2. 选择模型供应商（OpenAI/智谱AI/Anthropic）
3. 输入 API Key
4. 保存配置

---

## 📊 监控和日志

### 查看实时日志

在 Railway 控制台：
- 进入项目 → **Deployments**
- 点击最新的部署 → **View Logs**

### 监控资源使用

- 进入项目 → **Metrics**
- 查看 CPU、内存、网络使用情况

---

## 🔄 自动部署

配置完成后，每次推送到 GitHub `main` 分支时，Railway 会自动重新部署。

### 禁用自动部署（可选）

在项目设置 → **Settings** → **GitHub** 中关闭自动部署。

---

## ⚠️ 注意事项

1. **WebSocket 支持**：Railway 完全支持 WebSocket，无需额外配置
2. **免费额度**：Railway 提供 $5/月免费额度，适合测试和小规模使用
3. **数据库**：默认使用 SQLite，生产环境建议添加 PostgreSQL 服务
4. **环境变量**：生产环境务必使用强密钥
5. **CORS 配置**：确保添加正确的域名

---

## 🆚 添加 PostgreSQL（可选）

如果需要使用更强大的数据库：

### 在 Railway 中添加 PostgreSQL

1. 进入项目 → **New Service**
2. 选择 **Database** → **PostgreSQL**
3. Railway 会自动提供 `DATABASE_URL` 环境变量
4. 应用会自动检测并使用 PostgreSQL

---

## 📚 参考资源

- [Railway 官方文档](https://docs.railway.app/)
- [Railway Python 部署指南](https://docs.railway.app/deploying/python)
- [Railway 免费额度说明](https://docs.railway.app/pricing)

---

## 🆘 常见问题

### Q: 部署失败怎么办？

**A:** 查看部署日志，常见问题：
- Python 版本不兼容（需要 Python 3.10+）
- 依赖安装失败（检查 requirements.txt）
- 端口配置错误（确保使用 8000）

### Q: WebSocket 连接失败？

**A:** 检查：
1. CORS 配置是否包含 Railway 域名
2. Railway 是否正确启动了服务
3. 查看日志确认 WebSocket 服务正常

### Q: 如何设置自定义域名？

**A:**
1. 在 Railway 项目设置 → **Domains**
2. 添加自定义域名
3. 按照提示配置 DNS 记录

---

<p align="center">
  <b>祝部署顺利！如有问题请查看日志或提 Issue</b>
</p>
