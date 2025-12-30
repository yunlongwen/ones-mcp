#!/bin/bash

# ===================================
# ONES Wiki MCP Server - 简单部署脚本
# 直接运行 server_http_simple.py
# ===================================

set -e

echo "=================================="
echo "ONES Wiki MCP Server 部署"
echo "=================================="
echo ""

# 1. 检查 Python
echo "[1/3] 检查 Python..."
# 优先使用 python3.10，如果没有则使用 python3
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "✓ 使用 $(python3.10 --version)"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    echo "✓ 使用 $(python3 --version)"
    echo "⚠️  建议使用 Python 3.10+，当前版本可能不完全兼容"
else
    echo "✗ 未找到 python3 或 python3.10"
    echo "请先安装 Python 3.10+"
    exit 1
fi

# 2. 检查依赖
echo ""
echo "[2/4] 检查依赖..."
if $PYTHON_CMD -c "import mcp, aiohttp, starlette, uvicorn" 2>/dev/null; then
    echo "✓ 依赖已安装"
else
    echo "! 缺少依赖"
    
    # 尝试使用 pip 安装
    if $PYTHON_CMD -m pip install --user -r requirements.txt; then
        echo "✓ 依赖安装成功"
    else
        echo "✗ 依赖安装失败"
        echo ""
        echo "请手动安装依赖："
        echo "  $PYTHON_CMD -m pip install --user -r requirements.txt"
        echo ""
        exit 1
    fi
fi

# 3. 检查配置文件
echo ""
echo "[3/4] 检查配置文件..."
if [ ! -f "config.json" ]; then
    echo "警告: config.json 不存在，从示例复制..."
    cp config.example.json config.json
    echo "请编辑 config.json 后重新运行此脚本"
    exit 1
fi
echo "✓ config.json 存在"

# 4. 停止旧进程并启动服务
echo ""
echo "[4/4] 启动服务..."

# 停止旧进程
pkill -f "server_http_simple.py" 2>/dev/null || true
sleep 1

# 启动服务
echo "启动 server_http_simple.py..."
nohup $PYTHON_CMD server_http_simple.py > mcp-server.log 2>&1 &
PID=$!

sleep 2
if ps -p $PID > /dev/null; then
    echo "✓ 服务已启动 (PID: $PID)"
    echo ""
    echo "=================================="
    echo "部署完成！"
    echo "=================================="
    echo ""
    echo "服务信息:"
    echo "  PID: $PID"
    echo "  Python: $PYTHON_CMD"
    echo "  日志: mcp-server.log"
    echo "  地址: http://localhost:8000"
    echo "  SSE端点: http://localhost:8000/sse"
    echo ""
    echo "常用命令:"
    echo "  查看日志: tail -f mcp-server.log"
    echo "  停止服务: pkill -f server_http_simple"
    echo "  重启服务: bash deploy.sh"
    echo ""
else
    echo "✗ 服务启动失败"
    echo ""
    echo "查看日志:"
    tail -n 20 mcp-server.log
    echo ""
    exit 1
fi
