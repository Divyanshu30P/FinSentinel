import pytest
from backend.app.fraud_detection.risk_engine import UnifiedRiskEngine

def test_risk_scoring_empty():
    score, cat = UnifiedRiskEngine.calculate_score([])
    assert score == 0
    assert cat == "LOW"

def test_risk_scoring_critical_override():
    indicators = [
        {"code": "PIN_TO_RECEIVE", "title": "PIN To Receive", "severity": "CRITICAL", "description": "PIN requested to receive funds"}
    ]
    score, cat = UnifiedRiskEngine.calculate_score(indicators)
    assert score >= 78
    assert cat == "HIGH"

def test_risk_scoring_medium():
    indicators = [
        {"code": "UNEXPECTED_COLLECT", "title": "Unexpected", "severity": "MEDIUM", "description": "Unexpected"},
        {"code": "UNFAMILIAR_SENDER", "title": "Unfamiliar", "severity": "LOW", "description": "Unfamiliar"}
    ]
    score, cat = UnifiedRiskEngine.calculate_score(indicators)
    assert 20 <= score <= 69
    assert cat in ["LOW", "MEDIUM"]

def test_recommendations_generation():
    indicators = [
        {"code": "PIN_TO_RECEIVE", "title": "PIN To Receive", "severity": "CRITICAL", "description": "PIN requested"}
    ]
    recs = UnifiedRiskEngine.generate_recommendations("HIGH", indicators)
    assert any("UPI PIN" in r for r in recs)
    assert any("1930" in r or "cybercrime" in r for r in recs)
