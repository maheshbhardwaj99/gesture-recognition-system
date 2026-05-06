@echo off
echo.
echo ==================================================
echo   Gesture Recognition System - Setup and Run
echo ==================================================
echo.

where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b
)

echo Python found!

IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies (first time may take 1-2 min)...
pip install -q -r requirements.txt

echo.
echo Starting app...
echo.
echo    Open browser: http://localhost:5000
echo    Press Ctrl+C to stop
echo.

python app.py
pause
