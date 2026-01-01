@echo off
REM 启动 SheerID 验证工具 - Webhook 模式

echo ========================================
echo   SheerID Verification Tool
echo   Webhook 模式启动脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 检查依赖
echo [检查] 检查依赖...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [安装] 安装 Flask...
    pip install flask
)

REM 启动邮件接收服务器
echo.
echo [启动] 邮件接收服务器...
echo.
start "邮件接收服务" python email_receiver.py 5000

REM 等待服务器启动
timeout /t 3 /nobreak >nul

REM 启动主程序
echo.
echo [启动] 主验证程序...
echo.
python main.py

pause
