#!/bin/bash
# ClipNotes + ngrok 一键启动

echo "🚀 ClipNotes + ngrok 一键启动"
echo "================================"

# 检查 ngrok 是否安装
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok 未安装"
    echo ""
    echo "请安装 ngrok："
    echo "  brew install ngrok"
    echo "  或访问: https://ngrok.com/download"
    exit 1
fi

# 启动 ClipNotes 服务
echo ""
echo "1️⃣  启动 ClipNotes 服务..."
source .venv/bin/activate
uvicorn app_server:app --host 0.0.0.0 --port 8000 > /tmp/clipnotes.log 2>&1 &
CLIPNOTES_PID=$!
echo "   ✅ ClipNotes 已启动 (PID: $CLIPNOTES_PID)"

# 等待服务就绪
sleep 3

# 测试服务
if curl -s http://localhost:8000/healthz > /dev/null; then
    echo "   ✅ 服务健康检查通过"
else
    echo "   ❌ 服务启动失败，查看日志: tail -f /tmp/clipnotes.log"
    exit 1
fi

# 启动 ngrok
echo ""
echo "2️⃣  启动 ngrok（公网暴露）..."
ngrok http 8000 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
echo "   ✅ ngrok 已启动 (PID: $NGROK_PID)"

# 等待 ngrok 启动
sleep 3

# 获取公网 URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

echo ""
echo "================================"
echo "✅ 启动完成！"
echo "================================"
echo ""
echo "📍 本地地址:  http://localhost:8000"
echo "📍 公网地址:  $NGROK_URL"
echo ""
echo "🔗 在 ChatGPT 中配置 Action 时使用这个 URL："
echo "   $NGROK_URL"
echo ""
echo "📚 详细配置指南:"
echo "   cat CHATGPT_INTEGRATION.md"
echo ""
echo "🛑 停止服务:"
echo "   kill $CLIPNOTES_PID $NGROK_PID"
echo "   或运行: ./stop_all.sh"
echo ""
echo "📊 查看日志:"
echo "   tail -f /tmp/clipnotes.log   # ClipNotes 日志"
echo "   tail -f /tmp/ngrok.log       # ngrok 日志"
echo ""

# 保存 PID 供停止脚本使用
echo "$CLIPNOTES_PID" > /tmp/clipnotes.pid
echo "$NGROK_PID" > /tmp/ngrok.pid

echo "按 Ctrl+C 可以停止（或保持运行在后台）"
echo ""

# 保持脚本运行
wait
