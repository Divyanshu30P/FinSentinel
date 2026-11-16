import os
import re
import joblib
from typing import Dict, Any, List, Tuple
from ml.preprocessing import preprocess_text
from backend.app.fraud_detection.risk_engine import UnifiedRiskEngine

class PhishingDetector:
    """
    Detector for Phishing & Fraudulent Messages (Module 2).
    Combines NLP classification (TF-IDF + Logistic Regression)
    with deep rule-based heuristic indicators and suspicious span highlighting.
    """

    _model = None
    _vectorizer = None

    @classmethod
    def _load_model(cls):
        if cls._model is None or cls._vectorizer is None:
            model_path = os.path.join("ml", "saved_models", "phishing_model.joblib")
            vec_path = os.path.join("ml", "saved_models", "tfidf_vectorizer.joblib")
            if os.path.exists(model_path) and os.path.exists(vec_path):
                cls._model = joblib.load(model_path)
                cls._vectorizer = joblib.load(vec_path)
            else:
                print("Warning: Phishing ML model files not found. Using rule engine fallback.")

    RULE_PATTERNS = [
        # UPI PIN & OTP theft
        (r'\b(?:enter|share|send|provide)\s*(?:your)?(?:\s*[\w\-]+){0,3}\s*(?:upi\s*)?pin\b', "REQUEST_UPI_PIN", "CRITICAL",
         "Explicit request to share or enter UPI PIN. UPI PIN must never be revealed or entered to receive funds."),
        (r'\b(?:share|tell|send|enter|provide)\s*(?:your)?(?:\s*[\w\-]+){0,3}\s*otp\b', "REQUEST_OTP", "CRITICAL",
         "Solicitation of One-Time Password (OTP). Legitimate financial institutions never ask for OTPs."),
        
        # Threat of immediate disconnection / suspension
        (r'\b(?:electricity|power)\s*(?:will be|connection)\s*(?:disconnected|cut off|terminated)\b', "POWER_CUT_THREAT", "HIGH",
         "Electricity power disconnection threat lure, a high-frequency scam reported nationwide."),
        (r'\b(?:account|yono|netbanking|card|services?)\s*(?:has been|will be|is)\s*(?:blocked|suspended|deactivated|closed|restricted)\b', "ACCOUNT_SUSPENSION_THREAT", "HIGH",
         "Urgent threat of bank account suspension or debit card blocking."),
        (r'\b(?:update|verify|complete)\s*(?:your)?\s*(?:pan|aadhaar|kyc|biometric)\b', "KYC_COMPLIANCE_BAIT", "HIGH",
         "Urgent demand to update PAN, Aadhaar, or KYC to prevent penalty or block."),
        
        # Fake rewards / cashback / lottery
        (r'\b(?:won|reward|cashback|lottery|kbc|scratch card|prize)\s*(?:of|worth)?\s*(?:rs\.?|inr|₹)?\s*[\d,]+\b', "FAKE_REWARD_CLAIM", "HIGH",
         "Unsolicited claim of cash prize, lottery victory, or reward points redemption."),
        
        # Remote support / APK installation
        (r'\b(?:anydesk|teamviewer|quicksupport|rustdesk|\.apk|download\s+app)\b', "REMOTE_ACCESS_APK", "CRITICAL",
         "Request to install remote screen sharing tool or unverified Android APK package."),
         
        # Suspicious external links
        (r'https?://(?:[a-zA-Z0-9_\-]+\.)+(?:top|xyz|club|site|vip|info|in|net)(?:/[^\s]*)?|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+', "SUSPICIOUS_DOMAIN_OR_SHORTENER", "HIGH",
         "Contains a shortened or suspicious top-level domain frequently used in phishing landing pages.")
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        cls._load_model()

        indicators: List[Dict[str, Any]] = []
        highlighted_spans: List[str] = []

        # 1. Rule-based heuristic extraction
        for pattern, code, severity, desc in cls.RULE_PATTERNS:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                indicators.append({
                    "code": code,
                    "title": code.replace("_", " ").title(),
                    "severity": severity,
                    "description": desc
                })
                for match in matches:
                    highlighted_spans.append(match.group(0))

        # Check for generic URLs
        url_matches = re.findall(r'https?://[^\s]+|www\.[^\s]+', text)
        if url_matches and not any(ind["code"] == "SUSPICIOUS_DOMAIN_OR_SHORTENER" for ind in indicators):
            indicators.append({
                "code": "EXTERNAL_LINK_PRESENT",
                "title": "External Link Detected",
                "severity": "MEDIUM",
                "description": "Message contains external web link that should not be clicked before verification."
            })
            highlighted_spans.extend(url_matches)

        # 2. Machine Learning Pipeline Inference
        ml_probability = 0.0
        ml_prediction = "UNKNOWN"
        is_ml_applicable = False

        if cls._model is not None and cls._vectorizer is not None:
            cleaned = preprocess_text(text)
            features = cls._vectorizer.transform([cleaned])
            proba = cls._model.predict_proba(features)[0]
            # proba[1] is phishing class probability
            phishing_prob = float(proba[1])
            ml_probability = phishing_prob
            ml_prediction = "PHISHING" if phishing_prob >= 0.5 else "LEGITIMATE"
            is_ml_applicable = True

        # 3. Calculate calibrated unified risk score
        risk_score, risk_category = UnifiedRiskEngine.calculate_score(
            indicators=indicators,
            ml_probability=ml_probability if is_ml_applicable else 0.0,
            is_ml_applicable=is_ml_applicable
        )

        recommendations = UnifiedRiskEngine.generate_recommendations(risk_category, indicators)
        summary = text[:80] + ("..." if len(text) > 80 else "")

        return {
            "category": "PHISHING_MESSAGE",
            "input_summary": summary,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "detected_indicators": indicators,
            "ml_confidence": round(ml_probability, 4) if is_ml_applicable else None,
            "ml_prediction": ml_prediction,
            "highlighted_spans": list(set(highlighted_spans)),
            "recommendations": recommendations,
            "input_details": {"message_text": text}
        }
