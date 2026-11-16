import re
from typing import Dict, Any, List
from backend.app.schemas.fraud import CollectRequestInput
from backend.app.fraud_detection.risk_engine import UnifiedRiskEngine

class CollectRequestDetector:
    """
    Detector for Fake UPI Collect Requests (Module 1).
    Analyzes sender characteristics, payment descriptions, expectation flags,
    and PIN-related deception patterns.
    """

    SUSPICIOUS_DESCRIPTION_PATTERNS = [
        (r'\b(?:enter|type|input|enter\s+your)\s*(?:upi\s*)?pin\b', "PIN_TO_RECEIVE", "CRITICAL",
         "Instruction to enter UPI PIN to receive funds. Entering PIN always debits money."),
        (r'\b(?:receive|get|claim)\s*(?:money|cash|cashback|refund|prize|reward|amount)\b', "REWARD_CLAIM", "HIGH",
         "Collect request framed as receiving money, cashback, or reward."),
        (r'\b(?:lottery|kbc|lucky\s*draw|winner|congratulations)\b', "LOTTERY_BAIT", "HIGH",
         "Reference to lottery, prize draw, or reward contest."),
        (r'\b(?:olx|quikr|advance\s*payment|army|officer)\b', "MARKETPLACE_DECEPTION", "MEDIUM",
         "Common marketplace buyer scam phrasing (e.g. OLX advance payment / Army officer tactic)."),
        (r'\b(?:refund|reversal|chargeback|cashback)\b', "REFUND_CLAIM", "MEDIUM",
         "Unsolicited claim of pending refund or payment reversal."),
        (r'https?://[^\s]+|www\.[^\s]+|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+', "SUSPICIOUS_URL", "HIGH",
         "Collect request contains an external link or shortened URL.")
    ]

    SUSPICIOUS_VPA_PATTERNS = [
        (r'refund|support|helpdesk|verification|care|officer|winner|cashback', "IMPERSONATION_HANDLE", "MEDIUM",
         "VPA handle contains keywords often used to impersonate official support services.")
    ]

    @classmethod
    def analyze(cls, data: CollectRequestInput) -> Dict[str, Any]:
        indicators: List[Dict[str, Any]] = []
        combined_text = f"{data.request_description or ''} {data.associated_message or ''}".strip().lower()

        # 1. Expectation & Familiarity Analysis
        if not data.expected_request and not data.sender_known:
            indicators.append({
                "code": "UNEXPECTED_UNFAMILIAR",
                "title": "Unexpected Request from Unfamiliar Sender",
                "severity": "HIGH",
                "description": "Payment was not requested or expected by you, and the sender is unfamiliar."
            })
        elif not data.expected_request:
            indicators.append({
                "code": "UNEXPECTED_COLLECT",
                "title": "Unexpected Payment Request",
                "severity": "MEDIUM",
                "description": "You did not anticipate receiving this collect request."
            })
        elif not data.sender_known:
            # Note: Unfamiliar sender alone is NOT automatically fraudulent (as per requirements)
            indicators.append({
                "code": "UNFAMILIAR_SENDER",
                "title": "Unfamiliar Merchant / VPA",
                "severity": "LOW",
                "description": "The sender is not in your familiar contacts list. Verification advised."
            })

        # 2. Text Pattern Matching on Description & Instructions
        for pattern, code, severity, desc in cls.SUSPICIOUS_DESCRIPTION_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                indicators.append({
                    "code": code,
                    "title": code.replace("_", " ").title(),
                    "severity": severity,
                    "description": desc
                })

        # 3. VPA Handle Analysis
        vpa = (data.sender_vpa or "").strip().lower()
        for pattern, code, severity, desc in cls.SUSPICIOUS_VPA_PATTERNS:
            if re.search(pattern, vpa):
                indicators.append({
                    "code": code,
                    "title": "Suspicious VPA Identifier",
                    "severity": severity,
                    "description": desc
                })

        # 4. Amount-based heuristic
        if data.requested_amount >= 20000.0:
            indicators.append({
                "code": "HIGH_AMOUNT_REQUEST",
                "title": "High-Value Collect Request",
                "severity": "MEDIUM",
                "description": f"Requested amount (Rs {data.requested_amount:,.2f}) is substantial for an unverified collect request."
            })
        elif data.requested_amount in [1.0, 5.0, 10.0]:
            # Token test scam
            indicators.append({
                "code": "MICRO_VERIFICATION_TRAP",
                "title": "Micro-Transaction Verification Pattern",
                "severity": "LOW",
                "description": "Small token amounts (Rs 1-10) are sometimes used in fraudulent verification lures."
            })

        # Calculate final risk score
        risk_score, risk_category = UnifiedRiskEngine.calculate_score(
            indicators=indicators,
            ml_probability=0.0,
            is_ml_applicable=False
        )

        recommendations = UnifiedRiskEngine.generate_recommendations(risk_category, indicators)

        summary = f"Collect Request for Rs {data.requested_amount:,.2f} from {data.sender_vpa}"

        return {
            "category": "COLLECT_REQUEST",
            "input_summary": summary,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "detected_indicators": indicators,
            "ml_confidence": None,
            "recommendations": recommendations,
            "input_details": data.model_dump()
        }
