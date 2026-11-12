@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Atualizando as noticias da Central Robotica (pode levar alguns minutos)...
python coletor\gerenciador.py
echo.
echo Pronto. Recarregue a pagina para ver as novidades. Detalhes em logs\
pause
