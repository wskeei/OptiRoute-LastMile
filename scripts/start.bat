@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================================
:: OptiRoute Last-Mile — Windows One-Click Startup
:: Double-click this file to install all dependencies and start the system.
:: Prerequisites: Python 3.11+, Node.js 18+
:: ============================================================================

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"
set "WAIT_TIMEOUT=30"
set "PYTHON_MIN_MAJOR=3"
set "PYTHON_MIN_MINOR=11"
set "NODE_MIN_MAJOR=18"

:: Resolve project paths relative to this script (works when double-clicked)
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%\frontend"

:: ============================================================================
:: Header
:: ============================================================================
echo.
echo  ================================================================
echo          OptiRoute Last-Mile  -  Windows Launcher
echo       AI-Powered Last-Mile Delivery Dispatch System
echo  ================================================================
echo.

:: ============================================================================
:: Phase 1 — Detect required tools
:: ============================================================================
echo  [1/4] Checking system dependencies...
echo  ------------------------------------------------

:: --- Python ---
set "PYTHON="
set "PY_VER="
for /f "delims=" %%L in ('python --version 2^>nul') do set "PY_VER=%%L"
if defined PY_VER (
    for /f "tokens=2" %%V in ("!PY_VER!") do (
        for /f "tokens=1,2 delims=." %%A in ("%%V") do (
            set /a "PY_MAJOR=%%A" 2>nul
            set /a "PY_MINOR=%%B" 2>nul
            if !PY_MAJOR! geq %PYTHON_MIN_MAJOR% (
                if !PY_MINOR! geq %PYTHON_MIN_MINOR% set "PYTHON=python"
            )
        )
    )
)

if not defined PYTHON (
    echo  [X] Python %PYTHON_MIN_MAJOR%.%PYTHON_MIN_MINOR%+ NOT found.
    echo.
    echo      Please install Python 3.11+ from one of:
    echo        https://www.python.org/downloads/
    echo        Microsoft Store  ^(search "Python 3.11"^)
    echo.
    echo      IMPORTANT: Check "Add Python to PATH" during installation.
    echo      Then close and reopen this script.
    echo.
    pause
    exit /b 1
)
echo  [ok] Python !PY_VER!

:: --- Node.js ---
set "NODE="
set "NODE_VER="
set "NPM_VER="
for /f "delims=" %%L in ('node --version 2^>nul') do set "NODE_VER=%%L"
if defined NODE_VER (
    for /f "tokens=1 delims=." %%V in ("!NODE_VER!") do (
        set "NODE_MAJOR_RAW=%%V"
        set "NODE_MAJOR_RAW=!NODE_MAJOR_RAW:v=!"
        set /a "NODE_MAJOR=!NODE_MAJOR_RAW!" 2>nul
        if !NODE_MAJOR! geq %NODE_MIN_MAJOR% set "NODE=node"
    )
)

if not defined NODE (
    echo  [X] Node.js %NODE_MIN_MAJOR%+ NOT found.
    echo.
    echo      Please install Node.js LTS from:
    echo        https://nodejs.org/
    echo      Then close and reopen this script.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%V in ('npm --version 2^>nul') do set "NPM_VER=%%V"
echo  [ok] Node.js !NODE_VER!  (npm !NPM_VER!)

:: --- uv (Python package manager) ---
set "UV="
where uv >nul 2>&1 && set "UV=uv"

if not defined UV (
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "UV=%USERPROFILE%\.local\bin\uv.exe"
        set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    )
)

if not defined UV (
    echo.
    echo  [*] uv not found. Installing automatically...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://astral.sh/uv/install.ps1' -OutFile '$env:TEMP\uv_install.ps1'; & powershell -NoProfile -ExecutionPolicy Bypass -File '$env:TEMP\uv_install.ps1'"
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "UV=%USERPROFILE%\.local\bin\uv.exe"
        set "PATH=%USERPROFILE%\.local\bin;%PATH%"
        echo  [ok] uv installed successfully.
    ) else (
        echo  [X] uv auto-install failed.
        echo.
        echo      Please install manually by running in PowerShell:
        echo        irm https://astral.sh/uv/install.ps1 ^| iex
        echo.
        echo      Or visit: https://docs.astral.sh/uv/getting-started/installation/
        echo.
        pause
        exit /b 1
    )
)

set "UV_VER="
for /f "delims=" %%V in ('"%UV%" --version 2^>nul') do set "UV_VER=%%V"
echo  [ok] !UV_VER!
echo.

:: ============================================================================
:: Phase 2 — Install dependencies
:: ============================================================================
echo  [2/4] Installing project dependencies...
echo  ------------------------------------------------

:: --- Backend (Python via uv) ---
echo  [*] Backend: uv sync ...
pushd "%BACKEND_DIR%"
"%UV%" sync
if errorlevel 1 (
    popd
    echo  [X] Backend dependency installation failed.
    pause
    exit /b 1
)
popd
echo  [ok] Backend dependencies ready.

:: --- Frontend (Node.js via npm) ---
echo  [*] Frontend: npm install ...
pushd "%FRONTEND_DIR%"
if not exist node_modules (
    call npm install
) else (
    echo      node_modules exists - verifying with npm install.
    call npm install --prefer-offline
)
if errorlevel 1 (
    popd
    echo  [X] Frontend dependency installation failed.
    pause
    exit /b 1
)
popd
echo  [ok] Frontend dependencies ready.
echo.

:: ============================================================================
:: Phase 3 — Initialize database
:: ============================================================================
echo  [3/4] Initializing database...
echo  ------------------------------------------------

:: Remove old database files
del /f /q "%BACKEND_DIR%\sql_app.db" >nul 2>&1
del /f /q "%BACKEND_DIR%\sql_app.db-shm" >nul 2>&1
del /f /q "%BACKEND_DIR%\sql_app.db-wal" >nul 2>&1

:: Run Alembic migrations
echo  [*] Running database migrations...
pushd "%BACKEND_DIR%"
"%UV%" run alembic upgrade head
if errorlevel 1 (
    popd
    echo  [X] Database migration failed.
    pause
    exit /b 1
)
popd

:: Seed demo data
echo  [*] Seeding demo data...
pushd "%BACKEND_DIR%"
"%UV%" run python seed_shanghai_data.py
if errorlevel 1 (
    popd
    echo  [X] Data seeding failed.
    pause
    exit /b 1
)
popd
echo  [ok] Database initialized with demo data.
echo.

:: ============================================================================
:: Phase 4 — Start services
:: ============================================================================
echo  [4/4] Starting services...
echo  ------------------------------------------------

:: Check that ports are free
powershell -NoProfile -Command ^
    "$t = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, %BACKEND_PORT%); try { $t.Start(); $t.Stop() } catch { exit 1 }"
if errorlevel 1 (
    echo  [X] Port %BACKEND_PORT% is already in use. Please stop the existing process.
    pause
    exit /b 1
)
powershell -NoProfile -Command ^
    "$t = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, %FRONTEND_PORT%); try { $t.Start(); $t.Stop() } catch { exit 1 }"
if errorlevel 1 (
    echo  [X] Port %FRONTEND_PORT% is already in use. Please stop the existing process.
    pause
    exit /b 1
)

:: Launch backend in a new window
:: pushd sets the CWD for the start command, avoiding nested-quote path issues.
echo  [*] Starting backend server (port %BACKEND_PORT%)...
pushd "%BACKEND_DIR%"
start "OptiRoute Backend" cmd /k "title OptiRoute Backend ^& "%UV%" run uvicorn app.main:app --host 127.0.0.1 --port %BACKEND_PORT% --reload --reload-dir app"
popd

:: Launch frontend in a new window
echo  [*] Starting frontend dev server (port %FRONTEND_PORT%)...
pushd "%FRONTEND_DIR%"
start "OptiRoute Frontend" cmd /k "title OptiRoute Frontend ^& call npm run dev -- --host 127.0.0.1 --port %FRONTEND_PORT% --strictPort"
popd

:: Wait for services to be ready
echo.
echo  Waiting for services to start...
echo.

:: Wait for backend
set /a "_wb=0"
:_wait_backend
if !_wb! geq %WAIT_TIMEOUT% (
    echo  [!] Backend did not start within %WAIT_TIMEOUT%s. Check the backend window for errors.
    goto _done_wait
)
powershell -NoProfile -Command "try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect('127.0.0.1', %BACKEND_PORT%); $c.Close() } catch { exit 1 }"
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    set /a "_wb+=1"
    goto _wait_backend
)
echo  [ok] Backend is running.

:: Wait for frontend
set /a "_wf=0"
:_wait_frontend
if !_wf! geq %WAIT_TIMEOUT% (
    echo  [!] Frontend did not start within %WAIT_TIMEOUT%s. Check the frontend window for errors.
    goto _done_wait
)
powershell -NoProfile -Command "try { $c = New-Object System.Net.Sockets.TcpClient; $c.Connect('127.0.0.1', %FRONTEND_PORT%); $c.Close() } catch { exit 1 }"
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    set /a "_wf+=1"
    goto _wait_frontend
)
echo  [ok] Frontend is running.

:_done_wait

:: ============================================================================
:: Done — open browser
:: ============================================================================
echo.
echo  ================================================================
echo.
echo   System is ready!
echo.
echo     Frontend:  http://127.0.0.1:%FRONTEND_PORT%
echo     Backend:   http://127.0.0.1:%BACKEND_PORT%
echo     API Docs:  http://127.0.0.1:%BACKEND_PORT%/docs
echo.
echo   Close the "Backend" and "Frontend" terminal windows to stop.
echo   Or press Ctrl+C in each window.
echo.
echo  ================================================================
echo.

:: Open the frontend in the default browser
start "" "http://127.0.0.1:%FRONTEND_PORT%"

echo  Press any key to close this launcher window.
echo  (The Backend and Frontend windows will stay open.)
pause >nul
endlocal
