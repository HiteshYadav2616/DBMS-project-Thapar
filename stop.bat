@echo off
title Bus Registration - Stop All
color 0C

echo ============================================================
echo        BUS REGISTRATION PROJECT - STOPPING SERVERS
echo ============================================================
echo.

echo Stopping backend (uvicorn)...
taskkill /F /IM uvicorn.exe 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)

echo Stopping frontend (node/vite)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo All servers stopped.
pause

