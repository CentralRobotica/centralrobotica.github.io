@echo off
chcp 65001 >nul
echo Instalando o gerenciador automatico da Central Robotica...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_gerenciador.ps1"
echo.
pause
