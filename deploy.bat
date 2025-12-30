@echo off
REM ===================================
REM ONES Wiki MCP Server - Windows 一键部署
REM HTTP/SSE 多用户模式
REM ===================================

echo ================================
echo ONES Wiki MCP Server 一键部署
echo HTTP/SSE 多用户模式
echo ================================
echo.

REM 检查 Python
echo [1/4] 检查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo [成功] Python 已安装
echo.

REM 检查依赖
echo [2/4] 检查依赖...
python -c "import mcp, starlette, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 缺少依赖包，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖安装完成
) else (
    echo [成功] 依赖已安装
)
echo.

REM 检查配置文件
echo [3/4] 检查配置文件...
if not exist "config.json" (
    echo [提示] config.json 不存在，从示例复制...
    copy config.example.json config.json >nul
    echo [警告] 请先编辑 config.json 填入 ONES 系统信息！
    echo.
    echo 按任意键打开配置文件...
    pause >nul
    notepad config.json
    echo.
    echo 配置完成后按任意键继续...
    pause >nul
)
echo [成功] config.json 存在
echo.

REM 启动服务
echo [4/4] 启动 HTTP MCP 服务器...
echo [提示] 服务将在前台运行，按 Ctrl+C 停止
echo.
echo ================================
echo 服务信息
echo ================================
echo 地址: http://localhost:8001
echo SSE端点: http://localhost:8001/sse
echo 主页: http://localhost:8001/ (查看配置说明)
echo ================================
echo.
python server_http_simple.py

pause

