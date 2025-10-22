#!/bin/bash
# 停止所有服务

echo "🛑 停止 ClipNotes 和 ngrok..."

# 停止 ClipNotes
if [ -f /tmp/clipnotes.pid ]; then
    PID=$(cat /tmp/clipnotes.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null
        echo "   ✅ ClipNotes 已停止 (PID: $PID)"
    fi
    rm /tmp/clipnotes.pid
fi

# 停止所有 uvicorn 进程
pkill -f "uvicorn app_server:app" 2>/dev/null

# 停止 ngrok
if [ -f /tmp/ngrok.pid ]; then
    PID=$(cat /tmp/ngrok.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null
        echo "   ✅ ngrok 已停止 (PID: $PID)"
    fi
    rm /tmp/ngrok.pid
fi

# 停止所有 ngrok 进程
pkill -f "ngrok" 2>/dev/null

echo ""
echo "✅ 所有服务已停止"
