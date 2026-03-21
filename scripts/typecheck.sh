#!/bin/bash
# 类型检查脚本
# 用于快速检查 Python 代码的类型问题

echo "🔍 Running mypy type check..."
python -m mypy core/ --explicit-package-bases --no-error-summary "$@"
echo "✅ Type check complete"
