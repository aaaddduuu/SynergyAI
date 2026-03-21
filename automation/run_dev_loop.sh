#!/bin/bash

################################################################################
# SynergyAI 自动开发循环脚本
#
# 功能：循环调用 Claude Code 执行完整的开发流程
# 用法：./run_dev_loop.sh <次数>
# 示例：./run_dev_loop.sh 5  # 执行 5 次开发循环
################################################################################

# 不使用 set -e，因为我们需要自定义错误处理
# set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
# 脚本位于 automation/ 文件夹中，PROJECT_DIR 指向项目根目录（父目录）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/dev_loop_$(date +%Y%m%d_%H%M%S).log"
SERVER_PID_FILE="${PROJECT_DIR}/.server.pid"
SERVER_PORT=8000

# Claude Code 配置
CLAUDE_CMD="claude"  # Claude Code CLI 命令
INITIAL_PROMPT="请继续 SynergyAI 项目的开发工作。请从待办任务列表中选择一个优先级最高的任务来处理。遵循增量工作原则，一次只处理一个任务，完成后记得测试和提交。"

# 确保日志目录存在
mkdir -p "${LOG_DIR}"

################################################################################
# 日志函数
################################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $@" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "${LOG_FILE}"
}

log_step() {
    local step_num=$1
    local total_steps=$2
    shift 2
    echo -e "${PURPLE}[STEP ${step_num}/${total_steps}]${NC} $@" | tee -a "${LOG_FILE}"
}

log_divider() {
    echo "================================================================================" | tee -a "${LOG_FILE}"
}

################################################################################
# 进度条显示
################################################################################

show_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))

    printf "\r["
    printf "%${filled}s" | tr ' ' '='
    printf "%${empty}s" | tr ' ' ' '
    printf "] %d%% (%d/%d)" "${percent}" "${current}" "${total}"
}

################################################################################
# 启动开发服务器
################################################################################

start_server() {
    log_info "检查开发服务器状态..."

    if [ -f "${SERVER_PID_FILE}" ]; then
        local old_pid=$(cat "${SERVER_PID_FILE}")
        if ps -p "${old_pid}" > /dev/null 2>&1; then
            log_warning "服务器已在运行 (PID: ${old_pid})"
            return 0
        else
            log_info "清理旧的 PID 文件"
            rm -f "${SERVER_PID_FILE}"
        fi
    fi

    log_info "启动开发服务器 (端口 ${SERVER_PORT})..."

    # 检查端口是否被占用
    if lsof -i ":${SERVER_PORT}" > /dev/null 2>&1; then
        log_warning "端口 ${SERVER_PORT} 已被占用"
        log_info "尝试终止占用端口的进程..."
        local port_pid=$(lsof -ti ":${SERVER_PORT}" 2>/dev/null)
        if [ -n "$port_pid" ]; then
            kill -9 "$port_pid" 2>/dev/null || true
            sleep 2
            log_success "已终止占用端口的进程 (PID: ${port_pid})"
        fi
    fi

    # 启动服务器（后台运行）
    cd "${PROJECT_DIR}"
    local server_log="${LOG_DIR}/server_$(date +%Y%m%d_%H%M%S).log"
    nohup python main.py > "${server_log}" 2>&1 &
    local server_pid=$!
    echo ${server_pid} > "${SERVER_PID_FILE}"
    log_info "服务器进程已启动 (PID: ${server_pid}, 日志: ${server_log})"

    # 等待服务器启动
    log_info "等待服务器启动..."
    local max_wait=30
    local waited=0
    while [ ${waited} -lt ${max_wait} ]; do
        if curl -s "http://localhost:${SERVER_PORT}/api/health" > /dev/null 2>&1; then
            log_success "服务器启动成功 (PID: ${server_pid})"
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "."
    done
    echo ""

    # 启动失败，显示日志
    log_error "服务器启动超时"
    log_info "最近的日志输出:"
    tail -n 20 "${server_log}" | tee -a "${LOG_FILE}"
    return 1
}

################################################################################
# 停止开发服务器
################################################################################

stop_server() {
    log_info "停止开发服务器..."

    if [ ! -f "${SERVER_PID_FILE}" ]; then
        log_warning "未找到服务器 PID 文件"
        return 0
    fi

    local pid=$(cat "${SERVER_PID_FILE}")
    if ps -p "${pid}" > /dev/null 2>&1; then
        kill ${pid} 2>/dev/null || true
        sleep 1
        # 如果进程还在运行，强制终止
        if ps -p "${pid}" > /dev/null 2>&1; then
            log_warning "服务器未响应，强制终止..."
            kill -9 ${pid} 2>/dev/null || true
            sleep 1
        fi
        log_success "服务器已停止 (PID: ${pid})"
    else
        log_warning "服务器进程不存在 (PID: ${pid})"
    fi

    rm -f "${SERVER_PID_FILE}"
}

################################################################################
# 检查服务器健康状态
################################################################################

check_server_health() {
    if ! curl -s "http://localhost:${SERVER_PORT}/api/health" > /dev/null 2>&1; then
        log_warning "服务器不健康，尝试重启..."
        stop_server
        sleep 2
        if ! start_server; then
            log_error "服务器重启失败"
            return 1
        fi
        log_success "服务器重启成功"
    fi
    return 0
}

################################################################################
# 调用 Claude Code 执行开发任务
################################################################################

run_claude_development() {
    local iteration=$1
    local total=$2

    log_step 1 3 "调用 Claude Code 执行开发任务 (第 ${iteration}/${total} 轮)"

    # 记录开始时间
    local start_time=$(date +%s)

    # 检查 Claude Code 是否可用
    if ! command -v ${CLAUDE_CMD} > /dev/null 2>&1; then
        log_error "Claude Code CLI 未安装或不在 PATH 中"
        log_info "请安装 Claude Code CLI: npm install -g @anthropic-ai/claude-code"
        return 1
    fi

    # 构建 Claude Code 命令
    # 使用 -p/--print 模式进行非交互式执行
    log_info "执行 Claude Code..."

    # 执行 Claude Code
    local claude_log="${LOG_DIR}/claude_${iteration}_$(date +%Y%m%d_%H%M%S).log"
    if ${CLAUDE_CMD} -p --print "${INITIAL_PROMPT}" >> "${claude_log}" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local minutes=$((duration / 60))
        local seconds=$((duration % 60))

        log_success "第 ${iteration} 轮开发完成 (耗时: ${minutes}分${seconds}秒)"
        log_info "Claude Code 日志: ${claude_log}"

        # 将 Claude Code 日志追加到主日志
        cat "${claude_log}" >> "${LOG_FILE}" 2>&1 || true

        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local exit_code=$?

        log_error "第 ${iteration} 轮开发失败 (耗时: ${duration}秒, 退出码: ${exit_code})"
        log_info "Claude Code 日志: ${claude_log}"

        # 将 Claude Code 日志追加到主日志
        cat "${claude_log}" >> "${LOG_FILE}" 2>&1 || true

        # 显示最近的错误输出
        log_info "最近的错误输出:"
        tail -n 30 "${claude_log}" | tee -a "${LOG_FILE}"

        return 1
    fi
}

################################################################################
# 检查并提交代码变更
################################################################################

commit_changes() {
    local iteration=$1

    log_step 2 3 "检查代码变更并提交"

    cd "${PROJECT_DIR}"

    # 检查是否有变更
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_info "检测到代码变更，准备提交..."

        # 显示变更摘要
        log_info "变更文件:"
        git status --short | tee -a "${LOG_FILE}"

        # 添加所有变更
        git add -A

        # 创建提交信息
        local commit_msg="feat: 开发迭代 #${iteration} - 自动化开发流程

- 由 Claude Code 自动完成的功能开发
- 遵循增量工作原则
- 包含测试和验证

Commit: $(date +'%Y-%m-%d %H:%M:%S')
"

        # 提交变更
        if git commit -m "${commit_msg}" >> "${LOG_FILE}" 2>&1; then
            log_success "代码变更已提交"

            # 检查是否有远程仓库
            if git remote get-url origin > /dev/null 2>&1; then
                # 推送到远程仓库
                log_info "推送到远程仓库..."
                if git push origin main >> "${LOG_FILE}" 2>&1; then
                    log_success "代码已推送到远程仓库"
                else
                    log_warning "推送失败，请稍后手动推送"
                    log_info "可以使用以下命令手动推送: git push origin main"
                fi
            else
                log_warning "未配置远程仓库，跳过推送"
            fi
        else
            log_error "提交失败"
            return 1
        fi
    else
        log_info "没有检测到代码变更"
    fi

    return 0
}

################################################################################
# 生成进度报告
################################################################################

generate_report() {
    local total_iterations=$1
    local success_count=$2
    local failure_count=$3
    local start_time=$4
    local end_time=$5

    local total_duration=$((end_time - start_time))
    local hours=$((total_duration / 3600))
    local minutes=$(((total_duration % 3600) / 60))
    local seconds=$((total_duration % 60))

    log_divider
    log_success "==================== 开发循环完成报告 ===================="
    log_info "总迭代次数: ${total_iterations}"
    log_success "成功次数: ${success_count}"
    if [ ${failure_count} -gt 0 ]; then
        log_error "失败次数: ${failure_count}"
    fi
    log_info "总耗时: ${hours}小时${minutes}分${seconds}秒"
    if [ ${success_count} -gt 0 ]; then
        local avg_duration=$((total_duration / total_iterations))
        local avg_minutes=$((avg_duration / 60))
        local avg_seconds=$((avg_duration % 60))
        log_info "平均每轮: ${avg_minutes}分${avg_seconds}秒"
    fi
    log_info "日志文件: ${LOG_FILE}"
    log_divider
}

################################################################################
# 主函数
################################################################################

main() {
    # 检查参数
    if [ $# -ne 1 ]; then
        echo "用法: $0 <循环次数>"
        echo "示例: $0 5  # 执行 5 次开发循环"
        exit 1
    fi

    # 验证循环次数是正整数
    if ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 1 ]; then
        log_error "循环次数必须是正整数"
        exit 1
    fi

    local total_iterations=$1
    local success_count=0
    local failure_count=0
    local start_time=$(date +%s)

    # 打印欢迎信息
    clear
    log_divider
    echo -e "${CYAN}                    SynergyAI 自动开发循环${NC}"
    log_divider
    log_info "项目目录: ${PROJECT_DIR}"
    log_info "循环次数: ${total_iterations}"
    log_info "日志文件: ${LOG_FILE}"
    log_info "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_divider
    echo ""

    # 检查 Python 是否安装
    if ! command -v python > /dev/null 2>&1; then
        log_error "Python 未安装或不在 PATH 中"
        exit 1
    fi

    # 检查 main.py 是否存在
    if [ ! -f "${PROJECT_DIR}/main.py" ]; then
        log_error "未找到 main.py 文件"
        exit 1
    fi

    # 检查 git 是否初始化
    if [ ! -d "${PROJECT_DIR}/.git" ]; then
        log_warning "Git 仓库未初始化，代码提交功能将不可用"
    fi

    # 启动服务器
    if ! start_server; then
        log_error "无法启动服务器，退出"
        exit 1
    fi

    sleep 3  # 等待服务器完全启动

    # 主循环
    for ((i=1; i<=total_iterations; i++)); do
        log_divider
        echo -e "${CYAN}==================== 第 ${i}/${total_iterations} 轮开发循环 ====================${NC}" | tee -a "${LOG_FILE}"
        log_divider

        # 检查服务器健康状态
        if ! check_server_health; then
            log_error "服务器检查失败，跳过本轮"
            failure_count=$((failure_count + 1))
            continue
        fi

        # 执行开发任务
        if run_claude_development ${i} ${total_iterations}; then
            success_count=$((success_count + 1))

            # 提交变更
            commit_changes ${i}
        else
            failure_count=$((failure_count + 1))
            log_warning "本轮开发失败，继续下一轮..."
        fi

        # 显示进度
        echo ""
        show_progress ${i} ${total_iterations}
        echo ""

        # 如果不是最后一轮，等待一段时间再继续
        if [ ${i} -lt ${total_iterations} ]; then
            local wait_time=5
            log_info "等待 ${wait_time} 秒后开始下一轮..."
            sleep ${wait_time}
        fi
    done

    local end_time=$(date +%s)

    # 清理
    echo ""
    log_divider
    log_info "开发循环完成，清理资源..."
    stop_server

    # 生成报告
    generate_report ${total_iterations} ${success_count} ${failure_count} ${start_time} ${end_time}

    # 返回退出码
    if [ ${failure_count} -gt 0 ]; then
        log_warning "有 ${failure_count} 轮失败"
        exit 1
    else
        log_success "所有开发循环成功完成！"
        exit 0
    fi
}

# 捕获信号
cleanup_on_exit() {
    local exit_code=$?
    log_warning "收到退出信号 (退出码: ${exit_code})，停止服务器并清理..."
    stop_server
    exit ${exit_code}
}

trap cleanup_on_exit INT TERM

# 运行主函数
main "$@"
