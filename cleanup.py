"""
清理项目中的无用文件

包括：
- Python 缓存文件 (__pycache__, *.pyc)
- 测试生成的数据库文件 (test_*.db)
- 旧的日志文件
- 临时文件
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent


def cleanup_python_cache():
    """清理 Python 缓存文件"""
    print("[*] Cleaning Python cache files...")

    cache_dirs = list(BASE_DIR.rglob("__pycache__"))
    pyc_files = list(BASE_DIR.rglob("*.pyc"))

    removed_count = 0

    # 删除 __pycache__ 目录
    for cache_dir in cache_dirs:
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
            removed_count += 1
            print(f"  [+] Removed directory: {cache_dir.relative_to(BASE_DIR)}")

    # 删除 .pyc 文件
    for pyc_file in pyc_files:
        if pyc_file.is_file():
            pyc_file.unlink()
            removed_count += 1
            print(f"  [+] Removed file: {pyc_file.relative_to(BASE_DIR)}")

    print(f"  Total: {removed_count} cache files/directories removed\n")


def cleanup_test_databases():
    """清理测试数据库文件"""
    print("[*] Cleaning test database files...")

    data_dir = BASE_DIR / "data"
    if not data_dir.exists():
        print("  [!] data directory not found\n")
        return

    # 查找测试数据库
    test_dbs = []
    test_dbs.extend(data_dir.glob("test_*.db"))
    test_dbs.extend(data_dir.glob("test_integration_*.db"))
    test_dbs.extend(data_dir.glob("test_performance_*.db"))

    # 也删除 WAL 和 SHM 文件
    for db_file in test_dbs:
        wal_file = db_file.with_suffix(".db-wal")
        shm_file = db_file.with_suffix(".db-shm")
        if wal_file.exists():
            test_dbs.append(wal_file)
        if shm_file.exists():
            test_dbs.append(shm_file)

    removed_count = 0
    for test_file in test_dbs:
        if test_file.is_file():
            test_file.unlink()
            removed_count += 1
            print(f"  [+] Removed: {test_file.name}")

    print(f"  Total: {removed_count} test database files removed\n")


def cleanup_old_logs(days_to_keep=7):
    """清理旧日志文件"""
    print(f"[*] Cleaning log files older than {days_to_keep} days...")

    logs_dir = BASE_DIR / "logs"
    if not logs_dir.exists():
        print("  [!] logs directory not found\n")
        return

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    removed_count = 0

    # 查找所有 .log 文件
    log_files = list(logs_dir.glob("*.log"))

    for log_file in log_files:
        # 获取文件修改时间
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

        # 如果是旧日志，删除它
        if mtime < cutoff_date:
            log_file.unlink()
            removed_count += 1
            print(f"  [+] Removed: {log_file.name} ({mtime.strftime('%Y-%m-%d')})")

    # 特别处理 auto_dev_*.log 文件（这些通常是自动生成的）
    auto_dev_logs = list(logs_dir.glob("auto_dev_*.log"))
    for auto_log in auto_dev_logs:
        mtime = datetime.fromtimestamp(auto_log.stat().st_mtime)
        if mtime < cutoff_date:
            auto_log.unlink()
            removed_count += 1
            print(f"  [+] Removed: {auto_log.name} ({mtime.strftime('%Y-%m-%d')})")

    print(f"  Total: {removed_count} old log files removed\n")


def cleanup_temp_files():
    """清理其他临时文件"""
    print("[*] Cleaning temporary files...")

    temp_patterns = [
        "*.swp",
        "*.bak",
        "*.tmp",
        "*~",
        ".DS_Store",
        "Thumbs.db",
    ]

    removed_count = 0
    for pattern in temp_patterns:
        for temp_file in BASE_DIR.rglob(pattern):
            if temp_file.is_file():
                temp_file.unlink()
                removed_count += 1
                print(f"  [+] Removed: {temp_file.relative_to(BASE_DIR)}")

    if removed_count == 0:
        print("  [+] No temporary files found")
    else:
        print(f"  Total: {removed_count} temporary files removed\n")


def cleanup_coverage_files():
    """清理测试覆盖率文件"""
    print("[*] Cleaning test coverage files...")

    coverage_files = []
    coverage_files.extend(BASE_DIR.glob(".coverage"))
    coverage_files.extend(BASE_DIR.glob("htmlcov"))

    removed_count = 0
    for cov_file in coverage_files:
        if cov_file.is_dir():
            shutil.rmtree(cov_file)
            removed_count += 1
            print(f"  [+] Removed directory: {cov_file.name}")
        elif cov_file.is_file():
            cov_file.unlink()
            removed_count += 1
            print(f"  [+] Removed file: {cov_file.name}")

    if removed_count == 0:
        print("  [+] No coverage files found")
    else:
        print(f"  Total: {removed_count} coverage files/directories removed\n")


def cleanup_pytest_cache():
    """清理 pytest 缓存"""
    print("[*] Cleaning pytest cache...")

    pytest_cache = BASE_DIR / ".pytest_cache"
    if pytest_cache.exists() and pytest_cache.is_dir():
        shutil.rmtree(pytest_cache)
        print("  [+] Removed .pytest_cache directory\n")
    else:
        print("  [+] No pytest cache found\n")


def main():
    """主清理函数"""
    print("=" * 60)
    print("[*] Starting project cleanup")
    print("=" * 60)
    print()

    total_start = datetime.now()

    # 执行清理
    cleanup_python_cache()
    cleanup_test_databases()
    cleanup_old_logs(days_to_keep=7)
    cleanup_temp_files()
    cleanup_coverage_files()
    cleanup_pytest_cache()

    total_duration = (datetime.now() - total_start).total_seconds()

    print("=" * 60)
    print(f"[+] Cleanup completed! Time taken: {total_duration:.2f} seconds")
    print("=" * 60)
    print()
    print("[TIP] Run this script regularly to keep the project clean")
    print("[TIP] .gitignore is configured to ignore these files")


if __name__ == "__main__":
    main()
