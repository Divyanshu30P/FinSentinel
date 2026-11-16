import pytest
from backend.app.fraud_detection.phishing_detector import PhishingDetector

def test_electricity_bill_phishing():
    msg = "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210 or update now: http://power-bill-disconnection-alert.site/pay"
    result = PhishingDetector.analyze(msg)
    assert result["risk_category"] == "HIGH"
    assert result["risk_score"] >= 70
    codes = [ind["code"] for ind in result["detected_indicators"]]
    assert "POWER_CUT_THREAT" in codes
    assert len(result["highlighted_spans"]) > 0

def test_otp_theft_attempt():
    msg = "Dear Customer, share your 6-digit OTP to reverse failed payment of Rs 1500."
    result = PhishingDetector.analyze(msg)
    assert result["risk_category"] == "HIGH"
    codes = [ind["code"] for ind in result["detected_indicators"]]
    assert "REQUEST_OTP" in codes

def test_apk_remote_access_scam():
    msg = "To receive pending Swiggy refund, please download our official customer care tool anydesk.apk from http://support-desk.top/app"
    result = PhishingDetector.analyze(msg)
    assert result["risk_category"] == "HIGH"
    codes = [ind["code"] for ind in result["detected_indicators"]]
    assert "REMOTE_ACCESS_APK" in codes

def test_legitimate_bank_alert():
    msg = "HDFC Bank: Rs 450.00 debited from A/C XX4129 on 15-Nov-2026 to VPA zomato@hdfcbank (UPI Ref no 987654123012). Available Bal: Rs 45,210.00. Call 18002586161 if not you."
    result = PhishingDetector.analyze(msg)
    assert result["risk_category"] == "LOW"
    assert result["risk_score"] < 40
