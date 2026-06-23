#!/bin/bash
# 测试所有 Charts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== 测试所有 Charts ==="
echo ""

FAILED=0
PASSED=0

for chart_dir in "$REPO_ROOT/charts"/*; do
    if [ ! -d "$chart_dir" ]; then
        continue
    fi

    chart_name=$(basename "$chart_dir")
    echo "测试 $chart_name..."

    # Lint
    if helm lint "$chart_dir"; then
        echo "✓ $chart_name: lint 通过"
        PASSED=$((PASSED + 1))
    else
        echo "✗ $chart_name: lint 失败"
        FAILED=$((FAILED + 1))
    fi

    echo ""
done

echo "=== 测试结果 ==="
echo "通过: $PASSED"
echo "失败: $FAILED"

if [ $FAILED -gt 0 ]; then
    exit 1
fi
