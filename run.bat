@echo off
title UPI Shield - AI Financial Fraud Detection Platform
color 0A

:: Ensure working directory is the script directory
cd /d "%~dp0"

echo ======================================================================
echo              UPI SHIELD - FINANCIAL FRAUD DETECTION PLATFORM          
echo              AI-Powered Digital Payment Cybersecurity Defense         
echo ======================================================================
echo.

:: Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in system PATH.
    echo Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

:: Verify or train ML models if missing
if not exist "ml\saved_models\phishing_model.joblib" (
    echo [INFO] Training Phishing NLP Classifier...
    python ml\train_phishing_model.py
)

if not exist "ml\saved_models\isolation_forest.joblib" (
    echo [INFO] Training Transaction Anomaly Detection Model...
    python ml\transaction_anomaly.py
)

echo.
echo [INFO] Starting UPI Shield Server on http://127.0.0.1:8000
echo [INFO] API Swagger Documentation: http://127.0.0.1:8000/docs
echo.
echo Showcase Profile Credentials (Pre-seeded with Sample Scenarios):
echo Email:    demo@upishield.local
echo Password: DemoShield@2026
echo.
echo Note: You can also register a fresh personal account in Normal Mode.
echo ======================================================================
echo.

:: Launch the browser after a short delay in background
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

:: Start Uvicorn Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause
