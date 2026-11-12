@echo off
chcp 65001 >nul
echo ========================================
echo   供应商爬虫管理系统 - 安装依赖
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [✓] Python 已安装
python --version

:: 安装依赖
echo.
echo [1/3] 安装 Python 依赖包...
pip install fastapi uvicorn aiohttp beautifulsoup4 lxml apscheduler pydantic playwright browser_cookie3 pdfplumber pillow python-multipart
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] Python 依赖安装完成

:: 安装Playwright浏览器
echo.
echo [2/3] 安装 Playwright Chromium 浏览器（约300MB）...
python -m playwright install chromium
if errorlevel 1 (
    echo [警告] Playwright 安装失败，JS爬取功能将不可用
) else (
    echo [✓] Playwright 安装完成
)

:: 迁移数据（如果有MySQL）
echo.
echo [3/3] 是否从 MySQL 迁移现有数据？
set /p migrate="输入 y 迁移，直接回车跳过: "
if /i "%migrate%"=="y" (
    echo 正在迁移数据...
    python migrate_mysql_to_sqlite.py
)

echo.
echo ========================================
echo   安装完成！运行 start.bat 启动系统
echo ========================================
pause
