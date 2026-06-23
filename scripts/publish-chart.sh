#!/bin/bash
# 发布单个 Chart 到 gh-pages 分支

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查参数
if [ $# -eq 0 ]; then
    echo "Usage: $0 <chart-name>"
    echo ""
    echo "Available charts:"
    ls -1 "$REPO_ROOT/charts"
    exit 1
fi

CHART_NAME=$1
CHART_DIR="$REPO_ROOT/charts/$CHART_NAME"

# 验证 Chart 存在
if [ ! -d "$CHART_DIR" ]; then
    echo "❌ Chart not found: $CHART_NAME"
    echo "Available charts:"
    ls -1 "$REPO_ROOT/charts"
    exit 1
fi

echo "=== 发布 $CHART_NAME Chart ==="
echo ""

# 获取版本
CHART_VERSION=$(grep '^version:' "$CHART_DIR/Chart.yaml" | awk '{print $2}')
echo "Chart 版本: $CHART_VERSION"
echo ""

# 验证 Chart
echo "1. 验证 Chart..."
helm lint "$CHART_DIR"
if [ $? -ne 0 ]; then
    echo "❌ Chart 验证失败"
    exit 1
fi
echo "✓ Chart 验证通过"
echo ""

# 打包 Chart
echo "2. 打包 Chart..."
TEMP_DIR=$(mktemp -d)
helm package "$CHART_DIR" -d "$TEMP_DIR"
PACKAGE_FILE="$TEMP_DIR/${CHART_NAME}-${CHART_VERSION}.tgz"

if [ ! -f "$PACKAGE_FILE" ]; then
    echo "❌ 打包失败"
    exit 1
fi
echo "✓ 打包成功: ${CHART_NAME}-${CHART_VERSION}.tgz"
echo ""

# 切换到 gh-pages 分支
echo "3. 切换到 gh-pages 分支..."
cd "$REPO_ROOT"
git fetch origin
git checkout gh-pages
git pull origin gh-pages
echo "✓ 已在 gh-pages 分支"
echo ""

# 复制包文件
echo "4. 复制 Chart 包..."
cp "$PACKAGE_FILE" .
echo "✓ Chart 包已复制"
echo ""

# 更新索引
echo "5. 更新 Helm 索引..."
helm repo index . --url https://charts.binrc.com --merge index.yaml
echo "✓ 索引已更新"
echo ""

# 提交更改
echo "6. 提交到 Git..."
git add "${CHART_NAME}-${CHART_VERSION}.tgz" index.yaml
git commit -m "Release ${CHART_NAME}-${CHART_VERSION}

- Chart version: ${CHART_VERSION}
- Release date: $(date +%Y-%m-%d)
- Published from main branch
"
git push origin gh-pages
echo "✓ 已推送到 GitHub"
echo ""

# 清理
rm -rf "$TEMP_DIR"
git checkout main

echo "=== 发布完成！ ==="
echo ""
echo "Chart 已发布到: https://charts.binrc.com"
echo "Chart: ${CHART_NAME}"
echo "版本: ${CHART_VERSION}"
echo ""
echo "用户可以使用:"
echo "  helm repo add binrc https://charts.binrc.com"
echo "  helm repo update"
echo "  helm install ${CHART_NAME} binrc/${CHART_NAME} --version ${CHART_VERSION}"
