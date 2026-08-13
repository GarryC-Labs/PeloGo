#!/bin/bash
# PeloGo Setup Script for macOS/Linux
# This script sets up PeloGo and launches it

echo ""
echo "============================================================"
echo "                    PeloGo Setup (macOS/Linux)"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.10 or later:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-venv"
    echo ""
    exit 1
fi

echo "[OK] Python is installed"
python3 --version
echo ""

# Check if venv exists
if [ ! -d "env" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv env
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[OK] Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source env/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi
echo "[OK] Virtual environment activated"
echo ""

# Install requirements
echo "[INFO] Installing Python dependencies..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi
echo "[OK] Dependencies installed"
echo ""

# Check for ADB
echo "[INFO] Checking for ADB (Android Debug Bridge)..."
if ! command -v adb &> /dev/null; then
    echo "[WARNING] ADB is not installed or not in PATH"
    echo ""
    echo "To use PeloGo, you need ADB installed:"
    echo "  macOS: brew install android-platform-tools"
    echo "  Linux: sudo apt-get install android-tools-adb"
    echo ""
    echo "After installing ADB, run this script again"
    echo ""
    exit 1
fi
echo "[OK] ADB is installed"
adb version | grep "Android Debug Bridge"
echo ""

# Launch PeloGo
echo "============================================================"
echo "Starting PeloGo..."
echo "============================================================"
echo ""
echo "Open your browser to: http://localhost:5004"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
