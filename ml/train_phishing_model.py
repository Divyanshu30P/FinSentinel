"""
FinSentinel - Phishing Classification Model Training
Trains a TF-IDF Vectorizer + Logistic Regression pipeline
Evaluates real test set performance metrics and persists the model.
"""

import json
import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from ml.preprocessing import preprocess_text

def train_and_evaluate():
    dataset_path = "ml/datasets/sms_phishing_dataset.csv"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # 1. Clean & Preprocess
    print("Preprocessing text data...")
    df["cleaned_text"] = df["text"].apply(preprocess_text)
    
    X = df["cleaned_text"]
    y = df["label"]
    
    # 2. Train-Test Split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"Training set: {len(X_train)} samples | Testing set: {len(X_test)} samples")
    
    # 3. TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=4000,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 4. Logistic Regression Classifier
    clf = LogisticRegression(C=2.0, max_iter=1000, random_state=42)
    clf.fit(X_train_vec, y_train)
    
    # 5. Evaluate on Holdout Test Set
    y_pred = clf.predict(X_test_vec)
    y_pred_proba = clf.predict_proba(X_test_vec)[:, 1]
    
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("\n--- Real Test Set Evaluation Metrics ---")
    print(f"Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"Confusion Matrix (TN, FP / FN, TP):\n{cm}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"]))
    
    # 6. Save Models & Metrics
    os.makedirs("ml/saved_models", exist_ok=True)
    
    joblib.dump(clf, "ml/saved_models/phishing_model.joblib")
    joblib.dump(vectorizer, "ml/saved_models/tfidf_vectorizer.joblib")
    
    metrics_data = {
        "model_name": "TF-IDF + Logistic Regression",
        "dataset_size": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": {
            "true_negatives": cm[0][0],
            "false_positives": cm[0][1],
            "false_negatives": cm[1][0],
            "true_positives": cm[1][1]
        },
        "vocabulary_size": len(vectorizer.vocabulary_)
    }
    
    with open("ml/saved_models/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
        
    print("Model, Vectorizer, and Metrics successfully saved in ml/saved_models/")

if __name__ == "__main__":
    train_and_evaluate()
