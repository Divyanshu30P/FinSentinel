from typing import List, Dict, Any, Tuple

class UnifiedRiskEngine:
    """
    Unified Risk Assessment Engine for FinSentinel.
    Combines rule-based indicators and ML predictions into a calibrated 0-100 risk score
    with human-explainable factor breakdown.
    """

    SEVERITY_WEIGHTS = {
        "CRITICAL": 45,
        "HIGH": 30,
        "MEDIUM": 18,
        "LOW": 8
    }

    @classmethod
    def calculate_score(
        cls,
        indicators: List[Dict[str, Any]],
        ml_probability: float = 0.0,
        is_ml_applicable: bool = False
    ) -> Tuple[int, str]:
        """
        Calculates normalized risk score from 0 to 100.
        Returns: (risk_score, risk_category)
        """
        # Sum rule weights
        rule_score = 0
        has_critical = False

        for ind in indicators:
            sev = ind.get("severity", "LOW").upper()
            weight = cls.SEVERITY_WEIGHTS.get(sev, 8)
            rule_score += weight
            if sev == "CRITICAL":
                has_critical = True

        # ML integration (if available and applicable)
        if is_ml_applicable and ml_probability is not None:
            # Calibrated combination: 60% rule indicators, 40% ML model
            ml_component = ml_probability * 100.0
            raw_score = (0.55 * rule_score) + (0.45 * ml_component)
        else:
            raw_score = float(rule_score)

        # Rule safeguards: Rules must not be diluted by uncalibrated ML baselines
        if has_critical:
            raw_score = max(raw_score, 78.0)
        elif rule_score >= 45:
            raw_score = max(raw_score, 72.0)
        elif rule_score >= 20:
            raw_score = max(raw_score, 45.0)

        # Clamp between 0 and 100
        final_score = int(min(max(round(raw_score), 0), 100))

        # Assign risk category
        if final_score >= 70:
            category = "HIGH"
        elif final_score >= 40:
            category = "MEDIUM"
        else:
            category = "LOW"

        return final_score, category

    @classmethod
    def generate_recommendations(cls, category: str, detected_indicators: List[Dict[str, Any]]) -> List[str]:
        recommendations = []
        codes = [ind.get("code") for ind in detected_indicators]

        if "PIN_TO_RECEIVE" in codes:
            recommendations.append("NEVER enter your UPI PIN to receive money. UPI PIN is solely used for DEBITING funds from your account.")
        if "UNEXPECTED_COLLECT" in codes:
            recommendations.append("Decline the collect request on your UPI app immediately. Do not tap approve.")
        if "SUSPICIOUS_URL" in codes or "APK_DOWNLOAD" in codes:
            recommendations.append("Do not click links or download APK files sent via SMS or messaging apps.")
        if "URGENCY_THREAT" in codes or "KYC_SUSPENSION" in codes:
            recommendations.append("Banks and power boards never threaten immediate disconnection via personal mobile numbers. Verify directly through official helpline.")
        if "UNUSUAL_VELOCITY" in codes:
            recommendations.append("Multiple rapid debits detected. Freeze your UPI ID and contact your bank helpline (or 1930) immediately if these were unauthorized.")

        # Default fallbacks based on risk tier
        if category == "HIGH":
            recommendations.append("Report this fraud attempt to National Cyber Crime Reporting Portal at cybercrime.gov.in or dial 1930.")
            recommendations.append("Block and report the sender VPA or phone number within your UPI application.")
        elif category == "MEDIUM":
            recommendations.append("Exercise caution. Verify the sender's identity through an independent, verified contact before proceeding.")
        else:
            recommendations.append("The request/message shows standard indicators, but always maintain caution and check payment details before entering your PIN.")

        return recommendations
