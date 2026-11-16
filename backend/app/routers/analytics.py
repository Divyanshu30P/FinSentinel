from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.analysis import FraudAnalysis
from backend.app.auth import get_current_user
from backend.app.schemas.analytics import RiskDistribution

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])

@router.get("/risk-distribution", response_model=RiskDistribution)
def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    high_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.risk_category == "HIGH"
    ).count()

    medium_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.risk_category == "MEDIUM"
    ).count()

    low_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.risk_category == "LOW"
    ).count()

    # Category counts
    collect_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.category == "COLLECT_REQUEST"
    ).count()

    phishing_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.category == "PHISHING_MESSAGE"
    ).count()

    tx_count = db.query(FraudAnalysis).filter(
        FraudAnalysis.user_id == user_id,
        FraudAnalysis.category == "TRANSACTION_ANOMALY"
    ).count()

    # Timeline activity (last 7 days)
    now = datetime.now(timezone.utc)
    timeline = []
    for day in range(6, -1, -1):
        target_date = (now - timedelta(days=day)).date()
        date_str = target_date.strftime("%d %b")
        
        # Count analyses on this date
        count = db.query(FraudAnalysis).filter(
            FraudAnalysis.user_id == user_id,
            func.date(FraudAnalysis.created_at) == target_date
        ).count()
        
        timeline.append({"date": date_str, "count": count})

    return {
        "high_risk": high_count,
        "medium_risk": medium_count,
        "low_risk": low_count,
        "categories": {
            "collect_requests": collect_count,
            "phishing_messages": phishing_count,
            "transactions": tx_count
        },
        "timeline": timeline
    }

@router.get("/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    distribution = get_risk_distribution(db, current_user)
    return {
        "status": "success",
        "data": distribution
    }
