@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usar_python
py -3 mock_catalogo.py
goto terminar
:usar_python
python mock_catalogo.py
:terminar
pause
