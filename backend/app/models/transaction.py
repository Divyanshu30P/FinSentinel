import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class TransactionRecord(Base):
    __tablename__ = "transaction_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(String(100), nullable=False)
    timestamp = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # DEBIT, CREDIT
    recipient_vpa = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    status = Column(String(50), default="SUCCESS")
    risk_score = Column(Integer, default=0)
    risk_category = Column(String(20), default="LOW")
    anomaly_flags = Column(Text, nullable=True)  # JSON serialized list of flags
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="transactions")
