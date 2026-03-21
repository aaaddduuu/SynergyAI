@echo off
REM Docker 构建和测试脚本 (Windows)

echo ==========================================
echo SynergyAI Docker 构建脚本
echo ==========================================

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未安装
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker 环境检查通过

REM 创建必要的目录
echo.
echo 创建必要的目录...
if not exist data mkdir data
if not exist logs mkdir logs

REM 构建镜像
echo.
echo 开始构建 Docker 镜像...
docker-compose build

if %errorlevel% neq 0 (
    echo [错误] 镜像构建失败
    pause
    exit /b 1
)

echo [OK] 镜像构建成功

REM 测试运行
echo.
echo 启动容器进行测试...
docker-compose up -d

REM 等待服务启动
echo.
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 健康检查
echo.
echo 检查服务健康状态...
curl -f http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 服务健康检查通过
) else (
    echo [错误] 服务健康检查失败
    echo 查看日志: docker-compose logs
    docker-compose down
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 构建和测试完成！
echo ==========================================
echo.
echo 访问地址: http://localhost:8000
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo.
pause
