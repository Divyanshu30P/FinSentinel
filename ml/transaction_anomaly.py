"""
FinSentinel - Transaction Anomaly Detection Model Training
Trains an Isolation Forest model on multi-dimensional transaction features:
Amount, Timing, Velocity, and Recipient Novelty.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute behavioral feature vectors from sequential transaction records.
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df["dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
    elif "date" in df.columns:
        df["dt"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["dt"] = pd.Timestamp.now()

    df = df.sort_values("dt").reset_index(drop=True)
    
    # Feature 1: Log Amount
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["log_amount"] = np.log1p(np.maximum(df["amount"], 0.0))
    
    # Feature 2 & 3: Hour & Night Indicator (1 AM to 5 AM)
    df["hour"] = df["dt"].dt.hour.fillna(12).astype(int)
    df["is_night"] = df["hour"].apply(lambda h: 1.0 if (1 <= h <= 5) else 0.0)
    
    # Feature 4: Velocity (transactions within 60 mins window)
    velocity = []
    for i, row in df.iterrows():
        current_time = row["dt"]
        if pd.isna(current_time):
            velocity.append(1.0)
            continue
        window_start = current_time - pd.Timedelta(minutes=60)
        # count prior transactions in window
        count = df.iloc[:i+1][(df.iloc[:i+1]["dt"] >= window_start) & (df.iloc[:i+1]["dt"] <= current_time)].shape[0]
        velocity.append(float(count))
    df["velocity_60m"] = velocity
    
    # Feature 5: Amount to historical mean ratio
    historical_mean = df["amount"].mean() if len(df) > 0 and df["amount"].mean() > 0 else 1000.0
    df["amount_ratio"] = df["amount"] / historical_mean
    
    # Feature 6: Recipient familiarity (0 if repeated, 1 if brand new recipient)
    seen_recipients = set()
    is_new = []
    vpa_col = "recipient_vpa" if "recipient_vpa" in df.columns else "sender_recipient"
    if vpa_col not in df.columns:
        for c in df.columns:
            if "recipient" in c.lower() or "sender" in c.lower() or "vpa" in c.lower():
                vpa_col = c
                break
    
    for _, row in df.iterrows():
        rec = str(row.get(vpa_col, "")).strip().lower()
        if rec in seen_recipients or not rec:
            is_new.append(0.0)
        else:
            is_new.append(1.0)
            seen_recipients.add(rec)
    df["is_new_recipient"] = is_new

    features = df[["log_amount", "hour", "is_night", "velocity_60m", "amount_ratio", "is_new_recipient"]]
    return features

def train_isolation_forest():
    from sklearn.ensemble import IsolationForest
    csv_path = "ml/datasets/sample_transactions.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Transactions dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)
    X = extract_features(df)
    
    print(f"Training Isolation Forest on {len(X)} transaction feature vectors...")
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.10,
        random_state=42
    )
    iso_forest.fit(X)
    
    # Evaluate predictions (-1 = anomaly, 1 = normal)
    preds = iso_forest.predict(X)
    scores = iso_forest.decision_function(X)
    
    anomalies_detected = (preds == -1).sum()
    print(f"Model fitted successfully! Identified {anomalies_detected} anomalies out of {len(X)} samples.")
    
    os.makedirs("ml/saved_models", exist_ok=True)
    joblib.dump(iso_forest, "ml/saved_models/isolation_forest.joblib")
    print("Saved Isolation Forest model to ml/saved_models/isolation_forest.joblib")

if __name__ == "__main__":
    train_isolation_forest()
