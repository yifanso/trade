#!/usr/bin/env bash
# 启动带有下载按钮的Web前端

echo "启动 QLib 量化回测Web前端..."
echo ""
echo "功能包括:"
echo "  ✓ 回测结果仪表盘"
echo "  ✓ 手动数据下载"
echo "  ✓ 📥 新增：数据下载管理（支持触发下载按钮）"
echo "  ✓ 回测执行"
echo ""

# 确保在项目根目录
cd "$(dirname "$0")" || exit

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python -m venv .venv"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 启动Flask应用
echo "🚀 启动Flask应用..."
echo "📍 访问地址: http://localhost:5000"
echo ""
echo "新增功能："
echo "  📥 数据下载管理: http://localhost:5000/download-manager"
echo ""

python examples/web_frontend.py
