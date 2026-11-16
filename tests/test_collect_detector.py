import pytest
from backend.app.schemas.fraud import CollectRequestInput
from backend.app.fraud_detection.collect_detector import CollectRequestDetector

def test_pin_to_receive_detection():
    data = CollectRequestInput(
        sender_name="Prize Office",
        sender_vpa="lottery.support@ybl",
        requested_amount=5000.0,
        request_description="Enter your UPI PIN to receive cash prize",
        expected_request=False,
        sender_known=False,
        associated_message="Please accept and type PIN immediately"
    )
    result = CollectRequestDetector.analyze(data)
    assert result["risk_category"] == "HIGH"
    assert result["risk_score"] >= 75
    codes = [ind["code"] for ind in result["detected_indicators"]]
    assert "PIN_TO_RECEIVE" in codes
    assert "UNEXPECTED_UNFAMILIAR" in codes

def test_legitimate_expected_collect():
    data = CollectRequestInput(
        sender_name="Electricity Board",
        sender_vpa="billdesk@sbi",
        requested_amount=1250.0,
        request_description="Monthly electricity utility bill",
        expected_request=True,
        sender_known=True,
        associated_message=None
    )
    result = CollectRequestDetector.analyze(data)
    assert result["risk_category"] == "LOW"
    assert result["risk_score"] < 40

def test_unfamiliar_only_is_not_high_risk():
    data = CollectRequestInput(
        sender_name="New Tea Stall",
        sender_vpa="teastall@okaxis",
        requested_amount=30.0,
        request_description="Morning Chai",
        expected_request=True,
        sender_known=False,
        associated_message=None
    )
    result = CollectRequestDetector.analyze(data)
    # Prompt requirement: Do not classify every unfamiliar sender as fraudulent
    assert result["risk_category"] == "LOW"
