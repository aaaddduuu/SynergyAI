# SynergyAI Docker 部署指南

本文档介绍如何使用 Docker 部署 SynergyAI 多智能体协作系统。

## 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [部署步骤](#部署步骤)
- [常用命令](#常用命令)
- [故障排除](#故障排除)
- [生产环境部署](#生产环境部署)

## 前置要求

### 必需软件

- **Docker**: >= 20.10
  - 下载地址: https://docs.docker.com/get-docker/
- **Docker Compose**: >= 2.0
  - 通常随 Docker Desktop 一起安装

### 验证安装

```bash
docker --version
docker-compose --version
```

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-coworker
```

### 2. 配置环境变量（可选）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，修改必要的配置
# 至少需要配置 OPENAI_API_KEY
```

### 3. 构建并启动

```bash
# 方式一：使用构建脚本（推荐）
chmod +x scripts/docker-build.sh
./scripts/docker-build.sh

# 方式二：手动执行
docker-compose up -d
```

### 4. 访问应用

打开浏览器访问: http://localhost:8000

## 配置说明

### 环境变量

主要环境变量说明：

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | 是 |
| `OPENAI_BASE_URL` | OpenAI API 基础 URL | https://api.openai.com/v1 | 否 |
| `LOG_LEVEL` | 日志级别 | INFO | 否 |
| `API_PORT` | API 服务端口 | 8000 | 否 |
| `SECRET_KEY` | 应用密钥 | - | 生产环境必填 |

完整配置说明请参考 `.env.example` 文件。

### 卷挂载

docker-compose.yml 中配置了以下卷挂载：

- `./data:/app/data` - SQLite 数据库持久化
- `./logs:/app/logs` - 日志文件持久化

## 部署步骤

### 开发环境

```bash
# 1. 启动服务
docker-compose up

# 2. 查看日志
docker-compose logs -f

# 3. 停止服务
docker-compose down
```

### 生产环境

```bash
# 1. 配置环境变量
cp .env.example .env
vim .env  # 修改生产环境配置

# 2. 后台启动
docker-compose up -d

# 3. 检查健康状态
docker-compose ps
curl http://localhost:8000/api/health

# 4. 查看日志
docker-compose logs -f synergyai
```

## 常用命令

### 容器管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f synergyai

# 进入容器
docker-compose exec synergyai bash
```

### 构建和更新

```bash
# 重新构建镜像
docker-compose build

# 强制重新构建（不使用缓存）
docker-compose build --no-cache

# 更新并重启
docker-compose up -d --build
```

### 数据管理

```bash
# 备份数据库
docker-compose exec synergyai cp data/synergyai.db data/backup_$(date +%Y%m%d_%H%M%S).db

# 清理数据（危险操作！）
docker-compose down -v  # 删除所有卷
```

## 故障排除

### 问题 1: 容器无法启动

**检查步骤：**

```bash
# 查看容器日志
docker-compose logs synergyai

# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 检查 Docker 状态
docker ps -a
```

**常见原因：**
- 端口 8000 被占用
- 环境变量配置错误
- Docker 服务未运行

### 问题 2: 健康检查失败

**检查步骤：**

```bash
# 手动执行健康检查
curl http://localhost:8000/api/health

# 查看详细日志
docker-compose logs synergyai | grep ERROR
```

### 问题 3: 数据库连接错误

**解决方案：**

```bash
# 确保数据目录存在且有权限
mkdir -p data
chmod 755 data

# 重新创建容器
docker-compose down
docker-compose up -d
```

### 问题 4: 镜像构建失败

**检查步骤：**

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

## 生产环境部署

### 安全建议

1. **修改默认密钥**
   ```bash
   # 生成随机密钥
   openssl rand -hex 32
   ```

2. **配置防火墙**
   ```bash
   # 只允许特定端口
   ufw allow 8000/tcp
   ```

3. **使用 HTTPS**
   - 配置 Nginx 反向代理
   - 使用 Let's Encrypt 证书

4. **限制资源使用**
   ```yaml
   # docker-compose.yml
   services:
     synergyai:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

### 性能优化

1. **使用多阶段构建**（已优化）
   - 减小镜像大小
   - 提高构建速度

2. **启用日志轮转**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

3. **配置健康检查**（已配置）
   - 自动重启失败容器
   - 监控服务状态

### 监控和日志

```bash
# 实时查看日志
docker-compose logs -f --tail=100 synergyai

# 导出日志
docker-compose logs synergyai > logs/synergyai_$(date +%Y%m%d).log

# 监控资源使用
docker stats synergyai_app
```

## 更新部署

```bash
# 1. 备份数据
cp data/synergyai.db data/backup_$(date +%Y%m%d).db

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建并启动
docker-compose up -d --build

# 4. 验证更新
curl http://localhost:8000/api/health
```

## 技术支持

如遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查 GitHub Issues
3. 提交新的 Issue（包含详细日志）

## 附录

### Docker 镜像信息

- **基础镜像**: python:3.12-slim
- **镜像大小**: ~200MB
- **包含服务**: Python 3.12, FastAPI, Uvicorn

### 目录结构

```
.
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore          # Docker 忽略文件
├── .env.example           # 环境变量模板
├── scripts/
│   ├── docker-build.sh    # Linux/Mac 构建脚本
│   └── docker-build.bat   # Windows 构建脚本
└── DEPLOYMENT.md          # 本文档
```

### 相关文档

- [README.md](README.md) - 项目总体介绍
- [FEATURE_LIST_SUMMARY.md](FEATURE_LIST_SUMMARY.md) - 功能列表
- [交接文档.md](交接文档.md) - 中文项目文档
