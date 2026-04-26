@echo off
title AuraSnap v2.0 Launcher
color 35

echo.
echo  ___  ___  ___  _  _  ___ 
echo ^| _ ^^| | _^^| ^|  __ ^^| ^^^| / / ^|
echo ^|    ^| ^|   ^| ^^^| _ ^^|^^^|^|   ^<  ^|
echo ^|_^^|_^^|_^^|___^^| ^|___/ /_/\^_\^|
echo   AuraSnap v2.0 -- Tauri+React
echo.

:: Activate venv
call "%~dp0venv\Scripts\activate.bat"

:: Start Python API in background
echo [1/2] Starting Python API Backend...
start "AuraSnap-API" /MIN python "%~dp0api.py"
timeout /t 2 /nobreak > nul

:: Start Vite frontend
echo [2/2] Starting React Frontend (Vite)...
cd /d "%~dp0aurasnap-ui"
start "AuraSnap-UI" /MIN npm run dev

echo.
echo  AuraSnap is running!
echo  Open: http://localhost:5173
echo.
timeout /t 2 /nobreak > nul
start http://localhost:5173
