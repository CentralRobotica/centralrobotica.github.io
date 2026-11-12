@echo off
chcp 65001 >nul
echo Removendo o gerenciador automatico local da Central Robotica...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0remover_gerenciador.ps1"
echo.
pause
