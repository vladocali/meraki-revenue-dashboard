@echo off
REM Competitor Collector Launcher
REM Windows Batch Script

echo.
echo  ========================================
echo   COMPETITOR COLLECTOR 🤖
echo  ========================================
echo.

set "PY_EXE="
set "PY_ARGS="

python --version >nul 2>&1
if not errorlevel 1 (
    set "PY_EXE=python"
    goto :python_found
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY_EXE=py"
    set "PY_ARGS=-3"
    goto :python_found
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%~fD\python.exe" (
        set "PY_EXE=%%~fD\python.exe"
        set "PY_ARGS="
        goto :python_found
    )
)

:python_found
if "%PY_EXE%"=="" (
    echo ❌ Python no está instalado o no está en PATH
    pause
    exit /b 1
)

echo ✅ Python detectado: %PY_EXE% %PY_ARGS%

cd /d "%~dp0"

echo.
echo 🚀 Iniciando recolector de competencia...
echo.
echo 💡 Capturará competencia cada 3 horas por defecto.
echo 💡 Presiona Ctrl+C para detener.
echo.

"%PY_EXE%" %PY_ARGS% main.py --competitor-scheduler

pause