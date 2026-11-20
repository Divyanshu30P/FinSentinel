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

:: Detect working Python interpreter with required dependencies
set "PYTHON_CMD="

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" -c "import fastapi, uvicorn" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
        goto :python_found
    )
)

py -3.14 -c "import fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.14"
    goto :python_found
)

python -c "import fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_found
)

:: If not found, try to locate Python and install dependencies once
echo [INFO] Dependencies not found. Installing requirements...
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
) else (
    set "PYTHON_CMD=python"
)
%PYTHON_CMD% -m pip install -r requirements.txt

:python_found
echo [INFO] Using Python: %PYTHON_CMD%
echo.

:: Train ML models if not already present
if not exist "ml\saved_models\phishing_model.joblib" (
    echo [INFO] Initializing Phishing NLP Classifier...
    %PYTHON_CMD% ml\train_phishing_model.py
)

if not exist "ml\saved_models\isolation_forest.joblib" (
    echo [INFO] Initializing Transaction Anomaly Detection Model...
    %PYTHON_CMD% ml\transaction_anomaly.py
)

echo [INFO] Starting FinSentinel on http://127.0.0.1:8000
echo.
echo Showcase Account Credentials:
echo   Email:    demo@finsentinel.local
echo   Password: FinSentinel@2026
echo.
echo (You can also register a fresh account in Normal Mode)
echo ======================================================================
echo.

:: Launch application runner (starts server and opens browser automatically)
%PYTHON_CMD% run.py

pause
