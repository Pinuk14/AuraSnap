@echo off
echo ===================================
echo        Starting AuraSnap...
echo ===================================
echo.

:: Check if the virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please ensure 'venv' exists.
    pause
    exit /b 1
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Run the main application
python Main.py

:: Pause so the user can see any error messages if it crashes
pause
