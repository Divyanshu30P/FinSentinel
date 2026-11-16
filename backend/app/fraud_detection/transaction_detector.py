import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ml.transaction_anomaly import extract_features
from backend.app.fraud_detection.risk_engine import UnifiedRiskEngine

class TransactionDetector:
    """
    Detector for Suspicious Transactions & Behavioral Anomalies (Module 3).
    Combines Isolation Forest ML model with velocity checks, off-hours analysis,
    and statistical deviations from user baseline.
    """

    _iso_forest = None

    @classmethod
    def _load_model(cls):
        if cls._iso_forest is None:
            model_path = os.path.join("ml", "saved_models", "isolation_forest.joblib")
            if os.path.exists(model_path):
                cls._iso_forest = joblib.load(model_path)
            else:
                print("Warning: Isolation Forest model file not found. Using statistical rules.")

    @classmethod
    def analyze_batch(cls, df: pd.DataFrame) -> Dict[str, Any]:
        cls._load_model()

        if df.empty:
            return {"summary": {"total": 0, "anomalies": 0}, "results": []}

        # Normalize column names
        col_map = {}
        for c in df.columns:
            cleaned = c.strip().lower().replace(" ", "_").replace("-", "_")
            if "id" in cleaned and "tx" not in col_map:
                col_map[c] = "transaction_id"
            elif ("date" in cleaned or "time" in cleaned) and "timestamp" not in col_map:
                col_map[c] = "timestamp"
            elif "amount" in cleaned:
                col_map[c] = "amount"
            elif "type" in cleaned:
                col_map[c] = "transaction_type"
            elif ("recipient" in cleaned or "sender" in cleaned or "vpa" in cleaned) and "recipient_vpa" not in col_map:
                col_map[c] = "recipient_vpa"
            elif "desc" in cleaned:
                col_map[c] = "description"
            elif "status" in cleaned:
                col_map[c] = "status"

        df_norm = df.rename(columns=col_map).copy()

        # Defaults for missing columns
        if "transaction_id" not in df_norm.columns:
            df_norm["transaction_id"] = [f"TX{i+1001}" for i in range(len(df_norm))]
        if "timestamp" not in df_norm.columns:
            df_norm["timestamp"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        if "amount" not in df_norm.columns:
            df_norm["amount"] = 0.0
        if "transaction_type" not in df_norm.columns:
            df_norm["transaction_type"] = "DEBIT"
        if "recipient_vpa" not in df_norm.columns:
            df_norm["recipient_vpa"] = "N/A"
        if "description" not in df_norm.columns:
            df_norm["description"] = "N/A"
        if "status" not in df_norm.columns:
            df_norm["status"] = "SUCCESS"

        df_norm["amount"] = pd.to_numeric(df_norm["amount"], errors="coerce").fillna(0.0)

        # Baseline statistics
        mean_amount = float(df_norm["amount"].mean())
        std_amount = float(df_norm["amount"].std()) if len(df_norm) > 1 and not pd.isna(df_norm["amount"].std()) else 1.0

        # Feature extraction for Isolation Forest
        feature_df = extract_features(df_norm)
        
        iso_preds = None
        iso_scores = None
        if cls._iso_forest is not None:
            try:
                iso_preds = cls._iso_forest.predict(feature_df)  # -1 = anomaly, 1 = normal
                iso_scores = cls._iso_forest.decision_function(feature_df)
            except Exception as e:
                print(f"Isolation Forest inference error: {e}")

        results: List[Dict[str, Any]] = []
        high_risk_count = 0
        medium_risk_count = 0

        for i, row in df_norm.iterrows():
            amt = float(row["amount"])
            vpa = str(row["recipient_vpa"])
            desc = str(row["description"])
            tx_id = str(row["transaction_id"])
            ts = str(row["timestamp"])
            tx_type = str(row["transaction_type"])

            flags: List[str] = []
            indicators: List[Dict[str, Any]] = []

            # 1. Isolation Forest ML Anomaly Detection
            is_ml_anomaly = False
            if iso_preds is not None and iso_preds[i] == -1:
                is_ml_anomaly = True
                indicators.append({
                    "code": "ML_OUTLIER_DETECTED",
                    "title": "Machine Learning Anomaly Pattern",
                    "severity": "HIGH",
                    "description": "Multi-dimensional anomaly identified by Isolation Forest behavioral model."
                })
                flags.append("Isolation Forest Outlier")

            # 2. Velocity check (from feature_df)
            vel = float(feature_df.iloc[i]["velocity_60m"])
            if vel >= 3:
                indicators.append({
                    "code": "RAPID_TRANSACTION_BURST",
                    "title": f"High Velocity Burst ({int(vel)} transactions / hr)",
                    "severity": "HIGH",
                    "description": f"Observed {int(vel)} transactions in a short rolling window, indicative of rapid account draining."
                })
                flags.append(f"Rapid Velocity ({int(vel)} in 1hr)")

            # 3. Off-hours night check
            is_night = float(feature_df.iloc[i]["is_night"])
            if is_night == 1.0 and amt > 2000.0:
                indicators.append({
                    "code": "OFF_HOURS_HIGH_VALUE",
                    "title": "High-Value Late Night Transaction",
                    "severity": "MEDIUM",
                    "description": "Substantial debit occurred during uncustomary hours (1:00 AM - 5:00 AM)."
                })
                flags.append("Late Night (1-5 AM)")

            # 4. Statistical Deviation (Z-score > 2.5 or amount ratio > 5x)
            if std_amount > 0 and (amt - mean_amount) / std_amount > 2.5 and amt > 5000:
                indicators.append({
                    "code": "STATISTICAL_SPIKE",
                    "title": "Significant Deviation from Historical Average",
                    "severity": "HIGH",
                    "description": f"Amount Rs {amt:,.2f} deviates significantly from user's average spending (Rs {mean_amount:,.2f})."
                })
                flags.append("High Statistical Deviation")

            # 5. Suspicious recipient keyword or collect description
            suspicious_keywords = ["crypto", "winner", "lottery", "cashback", "refund", "fastcash", "telegram"]
            if any(k in vpa.lower() or k in desc.lower() for k in suspicious_keywords):
                indicators.append({
                    "code": "HIGH_RISK_RECIPIENT",
                    "title": "High-Risk Merchant / Keyword Detected",
                    "severity": "HIGH",
                    "description": f"Recipient identifier or description contains high-risk fraud keywords ({vpa})."
                })
                flags.append("High-Risk Merchant Category")

            # Calculate score
            score, cat = UnifiedRiskEngine.calculate_score(
                indicators=indicators,
                ml_probability=0.85 if is_ml_anomaly else 0.1,
                is_ml_applicable=True
            )

            if cat == "HIGH":
                high_risk_count += 1
            elif cat == "MEDIUM":
                medium_risk_count += 1

            # Contextual explanation
            if cat == "HIGH":
                explanation = f"Flagged as HIGH RISK due to {', '.join(flags) if flags else 'severe anomalous features'}. Review immediately."
            elif cat == "MEDIUM":
                explanation = f"Flagged as MEDIUM RISK due to {', '.join(flags) if flags else 'moderate deviations'}. Confirm authorization."
            else:
                explanation = "Transaction aligns with normal baseline patterns with no anomalous indicators."

            results.append({
                "transaction_id": tx_id,
                "timestamp": ts,
                "amount": amt,
                "transaction_type": tx_type,
                "recipient_vpa": vpa,
                "description": desc,
                "risk_score": score,
                "risk_category": cat,
                "anomaly_flags": flags,
                "is_anomaly": is_ml_anomaly or len(flags) > 0,
                "explanation": explanation
            })

        summary = {
            "total_transactions": len(results),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": len(results) - (high_risk_count + medium_risk_count),
            "anomalies_detected": high_risk_count + medium_risk_count,
            "average_amount": round(mean_amount, 2)
        }

        return {
            "summary": summary,
            "results": results
        }
