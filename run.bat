@echo off
title UPI Shield - AI Financial Fraud Detection Platform
color 0A

echo ======================================================================
echo              UPI SHIELD - FINANCIAL SCAM DETECTION PLATFORM          
echo              Arthaton: AI for Finance Hackathon Submission           
echo ======================================================================
echo.

:: Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in system PATH.
    echo Please install Python 3.10+ from python.org and try again.
    pause
    exit /b 1
)

:: Check if ML model is present; train if missing
if not exist "ml\saved_models\phishing_model.joblib" (
    echo [INFO] Training Phishing NLP Classifier (TF-IDF + Logistic Regression)...
    python ml\train_phishing_model.py
)

if not exist "ml\saved_models\isolation_forest.joblib" (
    echo [INFO] Training Transaction Anomaly Detection Model (Isolation Forest)...
    python ml\transaction_anomaly.py
)

echo.
echo [INFO] Starting UPI Shield Backend & Frontend Server on http://127.0.0.1:8000 ...
echo [INFO] API Swagger Documentation available at http://127.0.0.1:8000/docs
echo.
echo Demo User Credentials for Hackathon Judges:
echo Email:    demo@upishield.local
echo Password: DemoShield@2026
echo ======================================================================
echo.

:: Launch the browser automatically after 2 seconds in background
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

:: Start Uvicorn Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause
