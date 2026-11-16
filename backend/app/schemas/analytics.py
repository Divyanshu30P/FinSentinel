from pydantic import BaseModel
from typing import List, Dict, Any

class RecentActivityItem(BaseModel):
    id: str
    category: str
    input_summary: str
    risk_score: int
    risk_category: str
    created_at: str

class AlertItem(BaseModel):
    id: str
    title: str
    description: str
    risk_category: str
    created_at: str

class DashboardSummary(BaseModel):
    total_analyses: int
    collect_requests_count: int
    phishing_messages_count: int
    transactions_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    recent_alerts: List[AlertItem]
    recent_analyses: List[RecentActivityItem]

class RiskDistribution(BaseModel):
    high_risk: int
    medium_risk: int
    low_risk: int
    categories: Dict[str, int]
    timeline: List[Dict[str, Any]]
