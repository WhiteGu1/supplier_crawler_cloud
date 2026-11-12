@echo off
chcp 65001 >nul
title 供应商爬虫管理系统
echo ========================================
echo   供应商爬虫管理系统
echo   http://localhost:8100
echo   关闭此窗口即停止服务
echo ========================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先运行 install.bat
    pause
    exit /b 1
)

:: 自动打开浏览器（延迟3秒等服务启动）
start "" cmd /c "timeout /t 3 >nul && start http://localhost:8100"

:: 启动后端
cd api
python main.py

pause
