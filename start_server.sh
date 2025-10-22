#!/bin/bash
# ClipNotes 启动脚本

echo "🚀 启动 ClipNotes 服务..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 检查环境配置
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
fi

# 激活虚拟环境并启动服务
source .venv/bin/activate

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用"
    echo "   运行 './stop_server.sh' 停止旧服务，或使用其他端口"
    exit 1
fi

echo "✅ 启动服务在 http://localhost:8000"
echo "   按 Ctrl+C 停止服务"
echo ""

uvicorn app_server:app --host 0.0.0.0 --port 8000 --reload
