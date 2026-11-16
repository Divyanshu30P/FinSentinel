import pytest
import pandas as pd
from backend.app.fraud_detection.transaction_detector import TransactionDetector

def test_empty_transaction_batch():
    df = pd.DataFrame()
    res = TransactionDetector.analyze_batch(df)
    assert res["summary"]["total"] == 0
    assert len(res["results"]) == 0

def test_anomaly_burst_detection():
    data = [
        {"transaction_id": "T1", "timestamp": "2026-11-15 02:40:00", "amount": 20000.0, "transaction_type": "DEBIT", "recipient_vpa": "crypto.vip@paytm", "description": "Quick P2P"},
        {"transaction_id": "T2", "timestamp": "2026-11-15 02:43:00", "amount": 25000.0, "transaction_type": "DEBIT", "recipient_vpa": "winner.cash@okaxis", "description": "Collect Approval"},
        {"transaction_id": "T3", "timestamp": "2026-11-15 02:47:00", "amount": 45000.0, "transaction_type": "DEBIT", "recipient_vpa": "fastcash@ybl", "description": "Wallet Drain"}
    ]
    df = pd.DataFrame(data)
    res = TransactionDetector.analyze_batch(df)
    assert res["summary"]["anomalies_detected"] >= 2
    assert res["summary"]["high_risk_count"] >= 2

def test_normal_daytime_transactions():
    data = [
        {"transaction_id": "T1", "timestamp": "2026-11-15 12:30:00", "amount": 150.0, "transaction_type": "DEBIT", "recipient_vpa": "swiggy@icici", "description": "Food"},
        {"transaction_id": "T2", "timestamp": "2026-11-15 19:45:00", "amount": 420.0, "transaction_type": "DEBIT", "recipient_vpa": "blinkit@kotak", "description": "Snacks"}
    ]
    df = pd.DataFrame(data)
    res = TransactionDetector.analyze_batch(df)
    assert res["summary"]["high_risk_count"] == 0
    for r in res["results"]:
        assert r["risk_category"] == "LOW"
