from typing import List, Dict, Any
from backend.app.services.gemini_service import GeminiService

class ExplanationEngine:
    """
    Produces plain-language, contextual explanations for any fraud analysis.
    Uses Gemini API when available; otherwise provides expert-curated deterministic explanations.
    """

    @classmethod
    async def get_explanation(
        cls,
        category: str,
        input_text: str,
        risk_category: str,
        risk_score: int,
        indicators: List[Dict[str, Any]]
    ) -> str:
        # 1. Attempt Gemini Generation if configured
        ai_text = await GeminiService.generate_explanation(
            category=category,
            input_text=input_text,
            risk_category=risk_category,
            risk_score=risk_score,
            indicators=indicators
        )
        if ai_text:
            return ai_text

        # 2. Expert Deterministic Fallback Generator
        ind_codes = [ind.get("code") for ind in indicators]

        if risk_category == "HIGH":
            reasons = []
            if "PIN_TO_RECEIVE" in ind_codes:
                reasons.append("it instructs you to enter your secret UPI PIN to receive funds (in UPI architecture, entering a PIN always debits your account, never credits it)")
            if "REQUEST_OTP" in ind_codes:
                reasons.append("it requests your private One-Time Password (OTP), which legitimate banks and payment apps never ask for")
            if "REMOTE_ACCESS_APK" in ind_codes:
                reasons.append("it urges you to install dangerous remote access software or an unverified APK package")
            if "POWER_CUT_THREAT" in ind_codes:
                reasons.append("it threatens imminent electricity disconnection tonight to induce panic and force an unauthorized payment")
            if "ACCOUNT_SUSPENSION_THREAT" in ind_codes or "KYC_COMPLIANCE_BAIT" in ind_codes:
                reasons.append("it fabricates an urgent bank account suspension or KYC lapse to trick you into visiting a phishing portal")
            if "UNEXPECTED_UNFAMILIAR" in ind_codes:
                reasons.append("it is an unexpected money collect request sent by an unfamiliar merchant VPA")
            if "RAPID_TRANSACTION_BURST" in ind_codes:
                reasons.append("it exhibits a rapid burst of high-value debits in short succession, typical of automated wallet draining")

            if reasons:
                explanation = f"This activity is classified as HIGH RISK because {'; additionally, '.join(reasons)}. Do not approve or engage."
            else:
                explanation = f"This activity scored {risk_score}/100 High Risk due to multiple critical security flags matching known Indian cyber fraud patterns. Avoid interacting with this request."

        elif risk_category == "MEDIUM":
            reasons = []
            if "UNEXPECTED_COLLECT" in ind_codes:
                reasons.append("the payment collect request was unexpected")
            if "UNFAMILIAR_SENDER" in ind_codes:
                reasons.append("the sender VPA is not in your recognized contacts")
            if "EXTERNAL_LINK_PRESENT" in ind_codes:
                reasons.append("the message directs you to an external website that requires independent verification")
            if "OFF_HOURS_HIGH_VALUE" in ind_codes:
                reasons.append("the transaction occurred during unusual late-night hours (1 AM - 5 AM)")

            if reasons:
                explanation = f"This activity is marked as MEDIUM RISK ({risk_score}/100) because {', and '.join(reasons)}. Please verify the counterparty before proceeding."
            else:
                explanation = f"This activity shows moderate deviations ({risk_score}/100). Exercise caution and double-check recipient details before entering your UPI PIN."

        else:
            explanation = "This communication or transaction appears consistent with standard legitimate patterns (Score: Low Risk). No active deception or threat indicators were detected."

        return explanation
