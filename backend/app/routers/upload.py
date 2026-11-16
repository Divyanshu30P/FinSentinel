import io
import json
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import FraudAnalysis
from backend.app.models.transaction import TransactionRecord
from backend.app.models.notification import FraudAlert
from backend.app.auth import get_current_user
from backend.app.services.ocr_service import OCRService
from backend.app.fraud_detection.transaction_detector import TransactionDetector

router = APIRouter(prefix="/upload", tags=["Uploads & Ingestion"])

@router.post("/screenshot")
async def upload_screenshot(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{file.content_type}'. Allowed formats: JPG, PNG, WEBP."
        )

    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Image size exceeds the maximum limit of {settings.MAX_IMAGE_SIZE_MB}MB."
        )

    result = OCRService.extract_text_from_bytes(content, filename=file.filename or "")
    if not result.get("success", False):
        raise HTTPException(status_code=422, detail=result.get("error", "Failed to extract text from image."))

    return {
        "filename": file.filename,
        "extracted_text": result["extracted_text"],
        "is_tesseract_installed": result.get("is_tesseract_installed", False),
        "notice": result.get("notice", "")
    }

@router.post("/transactions")
async def upload_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are supported for transaction statements.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV file contains no transaction records.")

    batch_res = TransactionDetector.analyze_batch(df)

    # Persist transactions
    for res in batch_res["results"]:
        rec = TransactionRecord(
            user_id=current_user.id,
            transaction_id=res["transaction_id"],
            timestamp=res["timestamp"],
            amount=res["amount"],
            transaction_type=res["transaction_type"],
            recipient_vpa=res["recipient_vpa"],
            description=res["description"],
            risk_score=res["risk_score"],
            risk_category=res["risk_category"],
            anomaly_flags=json.dumps(res["anomaly_flags"])
        )
        db.add(rec)

    # Log overall analysis record
    total_anomalies = batch_res["summary"]["anomalies_detected"]
    overall_cat = "HIGH" if batch_res["summary"]["high_risk_count"] > 0 else ("MEDIUM" if batch_res["summary"]["medium_risk_count"] > 0 else "LOW")
    overall_score = 90 if overall_cat == "HIGH" else (50 if overall_cat == "MEDIUM" else 15)

    summary_text = f"CSV Statement Upload: {len(df)} transactions ({total_anomalies} anomalies detected)"

    db_analysis = FraudAnalysis(
        user_id=current_user.id,
        category="TRANSACTION_ANOMALY",
        input_summary=summary_text,
        input_details=json.dumps({"filename": file.filename, "records": len(df), "anomalies": total_anomalies}),
        risk_score=overall_score,
        risk_category=overall_cat,
        detected_indicators=json.dumps([{"code": "CSV_STATEMENT_ANALYSIS", "title": f"{total_anomalies} Behavioral Anomalies Identified", "severity": overall_cat, "description": "Isolation Forest & statistical scan completed."}]),
        ml_confidence=0.88 if total_anomalies > 0 else 0.05,
        explanation=f"Processed bank statement '{file.filename}'. Found {batch_res['summary']['high_risk_count']} high-risk anomalies and {batch_res['summary']['medium_risk_count']} medium-risk deviations.",
        safety_recommendations=json.dumps(["Verify flagged transactions", "Contact bank immediately if unrecognized"]),
        is_demo=current_user.is_demo
    )
    db.add(db_analysis)

    if overall_cat in ["HIGH", "MEDIUM"]:
        alert = FraudAlert(
            user_id=current_user.id,
            title=f"Statement Anomaly Alert: {file.filename}",
            description=f"Identified {total_anomalies} suspicious transactions in uploaded statement.",
            risk_category=overall_cat,
            analysis_id=db_analysis.id
        )
        db.add(alert)

    db.commit()

    return batch_res
