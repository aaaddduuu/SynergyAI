@echo off
REM =============================================================================
REM SynergyAI 智能自动化开发脚本
REM
REM 功能：从 feature_list.json 自动领任务并调用 Claude Code 开发
REM 用法：auto_dev.bat [任务数量]
REM 示例：auto_dev.bat 5  # 执行 5 个任务
REM =============================================================================

setlocal enabledelayedexpansion

REM 配置
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..
set PYTHON_SCRIPT=%SCRIPT_DIR%auto_dev.py

REM 解析参数
set ITERATIONS=%1
if "%ITERATIONS%"=="" (
    set ITERATIONS=
)

REM 打印欢迎信息
cls
echo ================================================================================
echo                    SynergyAI 智能自动化开发
echo ================================================================================
echo 项目目录: %PROJECT_DIR%
if defined ITERATIONS (
    echo 执行任务数: %ITERATIONS%
) else (
    echo 执行任务数: 全部
)
echo 开始时间: %date% %time%
echo ================================================================================
echo.

REM 检查 Python
where python >NUL 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 检查 Claude Code CLI
where claude >NUL 2>&1
if errorlevel 1 (
    echo [ERROR] 未找到 Claude Code CLI，请先安装
    echo 访问: https://claude.ai/code
    pause
    exit /b 1
)

REM 运行 Python 脚本
if defined ITERATIONS (
    python "%PYTHON_SCRIPT%" --iterations %ITERATIONS% --project-dir "%PROJECT_DIR%"
) else (
    python "%PYTHON_SCRIPT%" --project-dir "%PROJECT_DIR%"
)

REM 检查结果
if errorlevel 1 (
    echo.
    echo [ERROR] 自动化开发失败
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESS] 自动化开发完成
    pause
    exit /b 0
)
