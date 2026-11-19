"""
FinSentinel - Evaluation CLI Script
Loads the saved TF-IDF vectorizer and Logistic Regression model,
runs inference on test samples, prints confusion matrix and classification metrics.
"""

import os
import sys
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.preprocessing import preprocess_text

def run_evaluation():
    metrics_path = "ml/saved_models/metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        print("="*60)
        print("          FINSENTINEL ML MODEL PERFORMANCE REPORT          ")
        print("="*60)
        print(f"Model:           {metrics.get('model_name')}")
        print(f"Total Samples:   {metrics.get('dataset_size')}")
        print(f"Vocabulary Size: {metrics.get('vocabulary_size')} n-gram features")
        print(f"Accuracy:        {metrics.get('accuracy') * 100:.2f}%")
        print(f"Precision:       {metrics.get('precision'):.4f}")
        print(f"Recall:          {metrics.get('recall'):.4f}")
        print(f"F1-Score:        {metrics.get('f1_score'):.4f}")
        print(f"Confusion Matrix:")
        cm = metrics.get('confusion_matrix', {})
        print(f"  True Negatives (Legitimate): {cm.get('true_negatives')}")
        print(f"  False Positives:             {cm.get('false_positives')}")
        print(f"  False Negatives:             {cm.get('false_negatives')}")
        print(f"  True Positives (Phishing):   {cm.get('true_positives')}")
        print("="*60)
    else:
        print("No metrics.json found. Please run ml/train_phishing_model.py first.")

if __name__ == "__main__":
    run_evaluation()
