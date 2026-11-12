@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================================
echo   正在启动 WhatsApp 供应商 PDF 自动监控与扫码窗口...
echo   首次运行请在弹出的 Chrome 窗口中扫码登录 WhatsApp
echo ========================================================
python run_whatsapp_monitor.py
pause
