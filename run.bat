@echo off
title FinSentinel - AI Financial Fraud Detection Platform
color 0A

:: Ensure working directory is the script directory
cd /d "%~dp0"

echo ======================================================================
echo              FINSENTINEL - FINANCIAL FRAUD DETECTION PLATFORM         
echo              AI-Powered Digital Payment Cybersecurity Defense         
echo ======================================================================
echo.

:: Detect which Python interpreter has dependencies installed
set PYTHON_CMD=

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" -c "import fastapi, uvicorn" >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD="%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
        goto :python_found
    )
)

py -3.14 -c "import fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3.14
    goto :python_found
)

python -c "import fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

:: If not found, check if python command exists
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in system PATH.
    echo Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

set PYTHON_CMD=python
echo [INFO] Installing required dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt

:python_found
echo [INFO] Using Python environment: %PYTHON_CMD%
echo.

:: Verify or train ML models if missing
if not exist "ml\saved_models\phishing_model.joblib" (
    echo [INFO] Training Phishing NLP Classifier...
    %PYTHON_CMD% ml\train_phishing_model.py
)

if not exist "ml\saved_models\isolation_forest.joblib" (
    echo [INFO] Training Transaction Anomaly Detection Model...
    %PYTHON_CMD% ml\transaction_anomaly.py
)

echo.
echo [INFO] Starting FinSentinel Server on http://127.0.0.1:8000
echo [INFO] API Documentation: http://127.0.0.1:8000/docs
echo.
echo Pre-seeded Showcase Profile Credentials:
echo Email:    demo@finsentinel.local
echo Password: FinSentinel@2026
echo.
echo Note: You can also register a fresh personal account in Normal Mode.
echo ======================================================================
echo.

:: Smart browser launcher: waits in background until port 8000 is open, then opens browser
start "" %PYTHON_CMD% -c "import socket, time, webbrowser; [time.sleep(1) for _ in range(40) if socket.socket().connect_ex(('127.0.0.1', 8000)) != 0]; webbrowser.open('http://127.0.0.1:8000')"

:: Start Uvicorn Server directly
%PYTHON_CMD% -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

pause
