@echo off
title Bus Registration - Project Launcher
color 0A

echo ============================================================
echo        BUS REGISTRATION PROJECT - STARTUP SCRIPT
echo ============================================================
echo.

:: -------------------------------------------------------
:: 1. Check prerequisites
:: -------------------------------------------------------
echo [1/6] Checking prerequisites...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Download from https://nodejs.org/
    pause
    exit /b 1
)

where mysql >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] MySQL CLI not found in PATH.
    echo          Make sure MySQL Server is running manually.
    echo.
)

echo        Python  - OK
echo        Node.js - OK
echo.

:: -------------------------------------------------------
:: 2. Start MySQL (if running as a Windows service)
:: -------------------------------------------------------
echo [2/6] Checking MySQL service...

sc query MySQL >nul 2>&1
if %ERRORLEVEL% equ 0 (
    sc query MySQL | find "RUNNING" >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo        Starting MySQL service...
        net start MySQL 2>nul
    ) else (
        echo        MySQL is already running.
    )
) else (
    sc query MySQL80 >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        sc query MySQL80 | find "RUNNING" >nul 2>&1
        if %ERRORLEVEL% neq 0 (
            echo        Starting MySQL80 service...
            net start MySQL80 2>nul
        ) else (
            echo        MySQL80 is already running.
        )
    ) else (
        echo        [INFO] MySQL service not found as "MySQL" or "MySQL80".
        echo               Make sure your MySQL server is running.
    )
)
echo.

:: -------------------------------------------------------
:: 3. Create database if it doesn't exist
:: -------------------------------------------------------
echo [3/6] Setting up database...
mysql -u root -pKirpa@123 -e "CREATE DATABASE IF NOT EXISTS bus_booking;" 2>nul
if %ERRORLEVEL% equ 0 (
    echo        Database "bus_booking" is ready.
    echo        Importing schema...
    mysql -u root -pKirpa@123 bus_booking < "%~dp0Database\bus_reservation.sql" 2>nul
    echo        Schema imported.
) else (
    echo        [WARNING] Could not connect to MySQL. Make sure it is running
    echo                  and the credentials in backend\.env are correct.
)
echo.

:: -------------------------------------------------------
:: 4. Set up backend virtual environment
:: -------------------------------------------------------
echo [4/6] Setting up backend...
cd /d "%~dp0backend"

if not exist .venv (
    echo        Creating Python virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo        Installing Python dependencies...
pip install -r requirements.txt --quiet 2>nul

echo        Running database migrations...
alembic upgrade head 2>nul
echo        Backend ready.
echo.

:: -------------------------------------------------------
:: 5. Set up frontend
:: -------------------------------------------------------
echo [5/6] Setting up frontend...
cd /d "%~dp0frontend"

if not exist node_modules (
    echo        Installing npm dependencies...
    npm install
) else (
    echo        node_modules already exists, skipping install.
)
echo        Frontend ready.
echo.

:: -------------------------------------------------------
:: 6. Launch both servers
:: -------------------------------------------------------
echo [6/6] Starting servers...
echo.
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo   Frontend : http://localhost:5173
echo.
echo ============================================================
echo   Close this window or press Ctrl+C to stop both servers.
echo ============================================================
echo.

:: Start backend in a new window
cd /d "%~dp0backend"
start "Backend - FastAPI" cmd /k ".venv\Scripts\activate.bat && uvicorn app.main:app --reload"

:: Start frontend in a new window
cd /d "%~dp0frontend"
start "Frontend - Vite" cmd /k "npm run dev"

:: Open browser after a short delay
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo Both servers launched in separate windows.
echo You can close this setup window now.
pause

