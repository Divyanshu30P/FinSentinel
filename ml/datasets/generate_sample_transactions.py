"""
UPI Shield - Sample Transaction Dataset Generator
Generates realistic Indian UPI & banking transaction statements
containing normal patterns (Swiggy, Groceries, Utility, P2P friends, Salary)
and intentional fraud scenarios (2:30 AM velocity drain, huge unverified collect, high-risk merchant).
"""

import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_transactions():
    base_time = datetime(2026, 11, 15, 9, 0, 0)
    
    # 25 normal transactions over 10 days
    normal_merchants = [
        ("swiggy@icici", "Swiggy Order Food", [280, 450, 620, 890], "DEBIT"),
        ("zomato@hdfcbank", "Zomato Food Delivery", [350, 520, 780], "DEBIT"),
        ("blinkit@kotak", "Blinkit Groceries", [420, 680, 1150, 1800], "DEBIT"),
        ("bses.bill@sbi", "BSES Electricity Bill", [1420], "DEBIT"),
        ("airtel.pay@airtel", "Airtel Fiber Broadband", [943], "DEBIT"),
        ("rahul.sharma@okaxis", "Dinner split with Rahul", [350, 700], "DEBIT"),
        ("priya.patel@okhdfcbank", "Shared cab fare", [180, 240], "DEBIT"),
        ("company.payroll@sbi", "Monthly Salary Credit", [85000], "CREDIT"),
        ("metro.recharge@dmrc", "Delhi Metro Card Top-up", [200, 500], "DEBIT"),
        ("amazon.pay@apl", "Amazon Shopping", [1299, 2499, 850], "DEBIT"),
        ("starbucks@icici", "Starbucks Coffee", [380, 750], "DEBIT"),
        ("motherdairy@paytm", "Daily Milk & Curd", [66, 132], "DEBIT"),
    ]

    records = []
    tx_counter = 1001

    current_date = base_time - timedelta(days=9)
    for day in range(9):
        # 2 to 3 transactions per day during normal daytime hours (9 AM - 10 PM)
        for _ in range(random.randint(2, 3)):
            merchant, desc, amounts, tx_type = random.choice(normal_merchants)
            amt = float(random.choice(amounts))
            hour = random.randint(9, 21)
            minute = random.randint(5, 55)
            tx_time = current_date.replace(hour=hour, minute=minute, second=random.randint(10, 50))
            
            records.append({
                "transaction_id": f"UPI{tx_counter}",
                "timestamp": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amt,
                "transaction_type": tx_type,
                "recipient_vpa": merchant,
                "description": desc,
                "status": "SUCCESS"
            })
            tx_counter += 1
        current_date += timedelta(days=1)

    # Inject Fraud Case 1: Night-time sudden rapid velocity drain (3 rapid transactions at 2:40 AM)
    fraud_time = datetime(2026, 11, 15, 2, 41, 10)
    records.append({
        "transaction_id": f"UPI{tx_counter}",
        "timestamp": fraud_time.strftime("%Y-%m-%d %H:%M:%S"),
        "amount": 19999.00,
        "transaction_type": "DEBIT",
        "recipient_vpa": "fastcash.winner77@paytm",
        "description": "UPI Collect Approval",
        "status": "SUCCESS"
    })
    tx_counter += 1

    fraud_time_2 = fraud_time + timedelta(minutes=4)
    records.append({
        "transaction_id": f"UPI{tx_counter}",
        "timestamp": fraud_time_2.strftime("%Y-%m-%d %H:%M:%S"),
        "amount": 25000.00,
        "transaction_type": "DEBIT",
        "recipient_vpa": "crypto.exchange.p2p@okaxis",
        "description": "Express Transfer P2P",
        "status": "SUCCESS"
    })
    tx_counter += 1

    fraud_time_3 = fraud_time + timedelta(minutes=8)
    records.append({
        "transaction_id": f"UPI{tx_counter}",
        "timestamp": fraud_time_3.strftime("%Y-%m-%d %H:%M:%S"),
        "amount": 49999.00,
        "transaction_type": "DEBIT",
        "recipient_vpa": "lottery.refund.claim@ybl",
        "description": "Authorization PIN entered",
        "status": "SUCCESS"
    })
    tx_counter += 1

    # Sort chronologically
    df = pd.DataFrame(records)
    df["dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("dt").drop(columns=["dt"])
    
    return df

if __name__ == "__main__":
    df = generate_sample_transactions()
    path = "ml/datasets/sample_transactions.csv"
    df.to_csv(path, index=False)
    # Also save a copy in frontend/assets/samples/ for instant one-click demo load and download
    df.to_csv("frontend/assets/samples/sample_transactions.csv", index=False)
    print(f"Generated {len(df)} sample transactions saved to {path} and frontend assets.")
