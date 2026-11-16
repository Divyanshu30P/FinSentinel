from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import FraudAnalysis
from backend.app.models.transaction import TransactionRecord
from backend.app.models.notification import FraudAlert
from backend.app.schemas.analytics import DashboardSummary
from backend.app.auth import get_current_user
from backend.app.services.demo_seed import reset_demo_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    total_analyses = db.query(FraudAnalysis).filter(FraudAnalysis.user_id == user_id).count()
    collect_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.category == "COLLECT_REQUEST"
    ).count()
    phishing_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.category == "PHISHING_MESSAGE"
    ).count()
    tx_analyses_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.category == "TRANSACTION_ANOMALY"
    ).count()
    total_tx_records = db.query(TransactionRecord).filter(TransactionRecord.user_id == user_id).count()

    high_risk_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.risk_category == "HIGH"
    ).count()
    medium_risk_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.risk_category == "MEDIUM"
    ).count()
    low_risk_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.risk_category == "LOW"
    ).count()

    recent_alerts_db = db.query(FraudAlert).filter(
        FraudAlert.user_id == user_id
    ).order_by(FraudAlert.created_at.desc()).limit(5).all()

    recent_alerts = [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "risk_category": a.risk_category,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for a in recent_alerts_db
    ]

    recent_analyses_db = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id
    ).order_by(FraudAnalysis.created_at.desc()).limit(7).all()

    recent_analyses = [
        {
            "id": a.id,
            "category": a.category,
            "input_summary": a.input_summary,
            "risk_score": a.risk_score,
            "risk_category": a.risk_category,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for a in recent_analyses_db
    ]

    return {
        "total_analyses": total_analyses,
        "collect_requests_count": collect_count,
        "phishing_messages_count": phishing_count,
        "transactions_count": total_tx_records if total_tx_records > 0 else tx_analyses_count,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "recent_alerts": recent_alerts,
        "recent_analyses": recent_analyses
    }

@router.post("/reset-demo")
def reset_demo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reset_demo_data(db, current_user)
    return {"message": "Demo data successfully reset to clean evaluation baseline"}
