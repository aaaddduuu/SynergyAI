#!/bin/bash
# Docker 构建和测试脚本

set -e

echo "=========================================="
echo "SynergyAI Docker 构建脚本"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker 环境检查通过${NC}"

# 创建必要的目录
echo -e "\n${YELLOW}创建必要的目录...${NC}"
mkdir -p data logs

# 构建镜像
echo -e "\n${YELLOW}开始构建 Docker 镜像...${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 镜像构建成功${NC}"
else
    echo -e "${RED}✗ 镜像构建失败${NC}"
    exit 1
fi

# 测试运行
echo -e "\n${YELLOW}启动容器进行测试...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 健康检查
echo -e "\n${YELLOW}检查服务健康状态...${NC}"
if curl -f http://localhost:8000/api/health &> /dev/null; then
    echo -e "${GREEN}✓ 服务健康检查通过${NC}"
else
    echo -e "${RED}✗ 服务健康检查失败${NC}"
    echo "查看日志: docker-compose logs"
    docker-compose down
    exit 1
fi

echo -e "\n${GREEN}=========================================="
echo "构建和测试完成！"
echo "==========================================${NC}"
echo -e "\n访问地址: ${YELLOW}http://localhost:8000${NC}"
echo -e "查看日志: ${YELLOW}docker-compose logs -f${NC}"
echo -e "停止服务: ${YELLOW}docker-compose down${NC}"
