@echo off
REM Revenue Management Dashboard Launcher
REM Windows Batch Script

echo.
echo  ========================================
echo   REVENUE MANAGEMENT DASHBOARD 🏨
echo  ========================================
echo.

REM Detect Python executable (PATH, py launcher, LocalAppData)
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
    echo.
    echo Soluciones:
    echo 1. Instalar Python desde https://www.python.org/
    echo 2. Marcar "Add Python to PATH" al instalar
    echo 3. Cerrar y abrir la terminal después de instalar
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado: %PY_EXE% %PY_ARGS%

"%PY_EXE%" %PY_ARGS% -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️ Streamlit no está instalado
    echo Instalando dependencias...
    "%PY_EXE%" %PY_ARGS% -m pip install streamlit plotly numpy pandas
)

REM Change to dashboard directory
cd /d "%~dp0dashboard"

echo.
echo 🚀 Iniciando Dashboard...
echo.
echo 📱 URL local: http://localhost:8501
echo 📱 URL produccion: https://www.merakihost.com/dashboard
echo.
echo 💡 Tip: Presiona Ctrl+C para detener
echo.

"%PY_EXE%" %PY_ARGS% -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false

pause
