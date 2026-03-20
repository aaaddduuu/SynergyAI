@echo off
REM =============================================================================
REM SynergyAI 自动开发循环脚本 (Windows 版本)
REM
REM 功能：循环调用 Claude Code 执行完整的开发流程
REM 用法：run_dev_loop.bat <次数>
REM 示例：run_dev_loop.bat 5  # 执行 5 次开发循环
REM =============================================================================

setlocal enabledelayedexpansion

REM 配置
REM 脚本位于 automation/ 文件夹中，PROJECT_DIR 指向项目根目录（父目录）
set PROJECT_DIR=%~dp0..
set LOG_DIR=%PROJECT_DIR%\logs
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set LOG_FILE=%LOG_DIR%\dev_loop_%TIMESTAMP%.log
set SERVER_PID_FILE=%PROJECT_DIR%\.server.pid
set SERVER_PORT=8000

REM Claude Code 配置
set CLAUDE_CMD=claude
set INITIAL_PROMPT=请继续 SynergyAI 项目的开发工作。请从待办任务列表中选择一个优先级最高的任务来处理。遵循增量工作原则，一次只处理一个任务，完成后记得测试和提交。

REM 确保日志目录存在
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 解析参数
if "%1"=="" (
    echo 用法: %0 ^<循环次数^>
    echo 示例: %0 5  # 执行 5 次开发循环
    exit /b 1
)

set TOTAL_ITERATIONS=%1
set SUCCESS_COUNT=0
set FAILURE_COUNT=0

REM 打印欢迎信息
cls
echo ================================================================================
echo                    SynergyAI 自动开发循环
echo ================================================================================
echo 项目目录: %PROJECT_DIR%
echo 循环次数: %TOTAL_ITERATIONS%
echo 日志文件: %LOG_FILE%
echo 开始时间: %date% %time%
echo ================================================================================
echo.

REM 记录开始时间
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set MY_DATE=%%c-%%a-%%b
set START_TIME=%time%

REM ==============================================================================
REM 主循环
REM ==============================================================================

for /l %%i in (1,1,%TOTAL_ITERATIONS%) do (
    echo ================================================================================ >> "%LOG_FILE%"
    echo ==================== 第 %%i/%TOTAL_ITERATIONS% 轮开发循环 ==================== >> "%LOG_FILE%"
    echo ================================================================================ >> "%LOG_FILE%"

    echo.
    echo ==================== 第 %%i/%TOTAL_ITERATIONS% 轮开发循环 ====================

    REM 1. 启动服务器（如果未运行）
    echo [INFO] 检查服务器状态...
    if exist "%SERVER_PID_FILE%" (
        set /p OLD_PID=<"%SERVER_PID_FILE%"
        tasklist /FI "PID eq !OLD_PID!" 2>NUL | find "!OLD_PID!" >NUL
        if errorlevel 1 (
            echo [INFO] 旧的服务器进程不存在，清理 PID 文件
            del "%SERVER_PID_FILE%"
        ) else (
            echo [INFO] 服务器已在运行
        )
    )

    if not exist "%SERVER_PID_FILE%" (
        echo [INFO] 启动开发服务器...
        start /B python main.py > "%LOG_DIR%\server_%TIMESTAMP%.log" 2>&1
        set SERVER_PID=%ERRORLEVEL%
        echo !SERVER_PID!> "%SERVER_PID_FILE%"

        echo [INFO] 等待服务器启动...
        timeout /t 5 /nobreak >NUL
    )

    REM 2. 调用 Claude Code
    echo [STEP 1/3] 调用 Claude Code 执行开发任务 (第 %%i/%TOTAL_ITERATIONS% 轮)

    set ITERATION_START=!time!

    REM 执行 Claude Code（根据实际情况调整参数）
    %CLAUDE_CMD% --yes --no-interactive --allow-permissions --prompt "%INITIAL_PROMPT%" "%PROJECT_DIR%" >> "%LOG_FILE%" 2>&1

    if errorlevel 1 (
        echo [ERROR] 第 %%i 轮开发失败
        set /a FAILURE_COUNT+=1
        goto :next_iteration
    )

    set ITERATION_END=!time!

    REM 计算持续时间（简化版）
    echo [SUCCESS] 第 %%i 轮开发完成

    REM 3. 检查并提交代码变更
    echo [STEP 2/3] 检查代码变更并提交

    cd /d "%PROJECT_DIR%"

    REM 检查是否有变更
    git diff --quiet >NUL 2>&1
    if errorlevel 1 (
        echo [INFO] 检测到代码变更，准备提交...

        REM 显示变更
        git status --short >> "%LOG_FILE%"

        REM 添加所有变更
        git add -A

        REM 创建提交
        git commit -m "feat: 开发迭代 #%%i - 自动化开发流程

- 由 Claude Code 自动完成的功能开发
- 遵循增量工作原则
- 包含测试和验证

Commit: %MY_DATE% %time%" >> "%LOG_FILE%" 2>&1

        if errorlevel 1 (
            echo [WARNING] 没有需要提交的变更
        ) else (
            echo [SUCCESS] 代码变更已提交

            REM 推送到远程
            echo [INFO] 推送到远程仓库...
            git push origin main >> "%LOG_FILE%" 2>&1
            if errorlevel 1 (
                echo [WARNING] 推送失败，请稍后手动推送
            ) else (
                echo [SUCCESS] 代码已推送到远程仓库
            )
        )
    ) else (
        echo [INFO] 没有检测到代码变更
    )

    set /a SUCCESS_COUNT+=1

    REM 显示进度
    set /a PERCENT=%%i*100/%TOTAL_ITERATIONS%
    echo.
    echo 进度: [!PERCENT!%%] (%%i/%TOTAL_ITERATIONS%)

    :next_iteration
    echo.

    REM 如果不是最后一轮，等待一段时间
    if %%i lss %TOTAL_ITERATIONS% (
        echo [INFO] 等待 5 秒后开始下一轮...
        timeout /t 5 /nobreak >NUL
    )
)

REM ==============================================================================
REM 清理和报告
REM ==============================================================================

echo.
echo ================================================================================
echo [INFO] 开发循环完成，清理资源...

REM 停止服务器
if exist "%SERVER_PID_FILE%" (
    set /p SERVER_PID=<"%SERVER_PID_FILE%"
    tasklist /FI "PID eq !SERVER_PID!" 2>NUL | find "!SERVER_PID!" >NUL
    if not errorlevel 1 (
        taskkill /F /PID !SERVER_PID! >NUL 2>&1
        echo [INFO] 服务器已停止
    )
    del "%SERVER_PID_FILE%"
)

REM 记录结束时间
set END_TIME=%time%

REM 生成报告
echo ================================================================================
echo [SUCCESS] ==================== 开发循环完成报告 ====================
echo [INFO] 总迭代次数: %TOTAL_ITERATIONS%
echo [SUCCESS] 成功次数: %SUCCESS_COUNT%
if %FAILURE_COUNT% GTR 0 (
    echo [ERROR] 失败次数: %FAILURE_COUNT%
)
echo [INFO] 开始时间: %START_TIME%
echo [INFO] 结束时间: %END_TIME%
echo [INFO] 日志文件: %LOG_FILE%
echo ================================================================================

REM 返回退出码
if %FAILURE_COUNT% GTR 0 (
    echo [WARNING] 有 %FAILURE_COUNT% 轮失败
    exit /b 1
) else (
    echo [SUCCESS] 所开发循环成功完成！
    exit /b 0
)
