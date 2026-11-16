import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class FraudAnalysis(Base):
    __tablename__ = "fraud_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # COLLECT_REQUEST, PHISHING_MESSAGE, TRANSACTION_ANOMALY
    input_summary = Column(String(255), nullable=False)
    input_details = Column(Text, nullable=True)  # JSON serialized input
    risk_score = Column(Integer, nullable=False)  # 0 to 100
    risk_category = Column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH
    detected_indicators = Column(Text, nullable=False)  # JSON serialized list of detected red flags
    ml_confidence = Column(Float, nullable=True)
    explanation = Column(Text, nullable=False)
    safety_recommendations = Column(Text, nullable=False)  # JSON serialized list of recommendations
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="analyses")
