@echo off
REM ====================================
REM AgriWaste to Worth - Windows Startup
REM ====================================

title AgriWaste to Worth - Full Project
color 0A

echo.
echo ======================================================
echo   ^|^|  AgriWaste to Worth - Full Project Startup
echo   ^|^|  Frontend + Backend + AI System + Chatbot
echo ======================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
    echo.
)

REM Show system info
echo [INFO] System Status:
python -c "import sys; print(f'  - Python: {sys.version.split()[0]}')"
echo.

REM Start the server
echo [INFO] Starting Flask Server...
echo [INFO] This will take a moment to initialize...
echo.

python startup.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start server
    echo.
    pause
    exit /b 1
)

pause
