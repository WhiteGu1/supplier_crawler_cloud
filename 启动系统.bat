@echo off
chcp 65001 >nul
title Supplier Crawler System

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11
    pause
    exit /b
)

cd /d "%~dp0"

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install aiohttp beautifulsoup4 lxml requests mysql-connector-python fastapi "uvicorn[standard]" pydantic APScheduler pandas python-dotenv tenacity fake-useragent Pillow playwright
    python -m playwright install chromium
)

echo Starting backend on port 8100...
start "Backend" cmd /k "cd /d "%~dp0api" && python main.py"

timeout /t 3 /nobreak >nul

echo Opening dashboard...
start "" "http://localhost:8100"

echo.
echo Backend : http://localhost:8100
echo API Docs: http://localhost:8100/docs
echo.
pause
