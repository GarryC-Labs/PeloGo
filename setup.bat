@echo off
REM PeloGo Setup Script for Windows
REM This script sets up PeloGo and launches it

echo.
echo ============================================================
echo                    PeloGo Setup (Windows)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or later from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if venv exists
if not exist "env\" (
    echo [INFO] Creating virtual environment...
    python -m venv env
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Install requirements
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check for ADB
echo [INFO] Checking for ADB (Android Debug Bridge)...
adb version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ADB is not installed or not in PATH
    echo.
    echo To use PeloGo, you need ADB installed:
    echo   https://developer.android.com/studio/releases/platform-tools
    echo.
    echo Download, extract, and add the folder to your PATH
    echo After installing ADB, restart this script
    echo.
    pause
    exit /b 1
)
echo [OK] ADB is installed
adb version | find "Android Debug Bridge"
echo.

REM Launch PeloGo
echo ============================================================
echo Starting PeloGo...
echo ============================================================
echo.
echo Open your browser to: http://localhost:5004
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
