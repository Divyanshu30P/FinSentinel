import json
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.auth import hash_password
from backend.app.models.user import User
from backend.app.models.analysis import FraudAnalysis
from backend.app.models.transaction import TransactionRecord
from backend.app.models.notification import FraudAlert

def seed_demo_data(db: Session) -> User:
    """
    Seeds initial showcase user, realistic fraud analyses, transaction records,
    and fraud alerts for testing and evaluation.
    """
    # 1. Find or create demo user
    demo_user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
    if not demo_user:
        demo_user = User(
            email=settings.DEMO_USER_EMAIL,
            username=settings.DEMO_USER_NAME,
            hashed_password=hash_password(settings.DEMO_USER_PASSWORD),
            is_demo=True
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    elif demo_user.username == "Hackathon Judge":
        demo_user.username = settings.DEMO_USER_NAME
        db.commit()

    # Check if demo analyses already exist
    existing_analyses = db.query(FraudAnalysis).filter(FraudAnalysis.user_id == demo_user.id).count()
    if existing_analyses > 0:
        return demo_user

    now = datetime.now(timezone.utc)

    # 2. Add realistic demo fraud analyses
    demo_analyses_data = [
        {
            "category": "COLLECT_REQUEST",
            "input_summary": "Collect Request for Rs 4,999.00 from cashback.rewards@okhdfcbank",
            "risk_score": 92,
            "risk_category": "HIGH",
            "input_details": json.dumps({
                "sender_name": "Diwali Reward Desk",
                "sender_vpa": "cashback.rewards@okhdfcbank",
                "requested_amount": 4999.0,
                "request_description": "Enter UPI PIN to receive Diwali cashback prize into your account",
                "expected_request": False,
                "sender_known": False
            }),
            "detected_indicators": json.dumps([
                {"code": "PIN_TO_RECEIVE", "title": "Pin To Receive", "severity": "CRITICAL", "description": "Instruction to enter UPI PIN to receive funds. Entering PIN always debits money."},
                {"code": "UNEXPECTED_UNFAMILIAR", "title": "Unexpected Request from Unfamiliar Sender", "severity": "HIGH", "description": "Payment was not requested or expected by you, and the sender is unfamiliar."},
                {"code": "REWARD_CLAIM", "title": "Reward Claim", "severity": "HIGH", "description": "Collect request framed as receiving money, cashback, or reward."}
            ]),
            "ml_confidence": None,
            "explanation": "This collect request is HIGH RISK (Score 92/100). The sender claims you will receive a cashback, but in UPI architecture, typing your UPI PIN authorises a DEBIT from your bank account, not a credit. Approving this request will immediately transfer Rs 4,999 to the fraudster.",
            "safety_recommendations": json.dumps([
                "NEVER enter your UPI PIN to receive money.",
                "Decline this collect request immediately in your UPI application.",
                "Report this VPA handle on the National Cyber Crime Reporting Portal (1930)."
            ]),
            "created_at": now - timedelta(hours=2)
        },
        {
            "category": "PHISHING_MESSAGE",
            "input_summary": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM...",
            "risk_score": 96,
            "risk_category": "HIGH",
            "input_details": json.dumps({
                "message_text": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210 or update now: http://power-bill-disconnection-alert.site/pay"
            }),
            "detected_indicators": json.dumps([
                {"code": "POWER_CUT_THREAT", "title": "Power Cut Threat", "severity": "HIGH", "description": "Electricity power disconnection threat lure, a high-frequency scam reported nationwide."},
                {"code": "SUSPICIOUS_DOMAIN_OR_SHORTENER", "title": "Suspicious Domain Or Shortener", "severity": "HIGH", "description": "Contains a shortened or suspicious top-level domain frequently used in phishing landing pages."}
            ]),
            "ml_confidence": 0.9942,
            "explanation": "The message was classified as HIGH RISK Phishing (96/100) by our NLP classifier and heuristic engine. Disconnection threats sent via personal SMS are standard social engineering tactics. Official electricity boards never ask consumers to call random 10-digit mobile numbers or make payments through unverified web links.",
            "safety_recommendations": json.dumps([
                "Do not click the link or dial the mobile number provided.",
                "Check your bill status exclusively on the official state electricity board website or app.",
                "Forward the SMS to 1909 (Do Not Disturb registry) to report telecom spam."
            ]),
            "created_at": now - timedelta(hours=5)
        },
        {
            "category": "PHISHING_MESSAGE",
            "input_summary": "HDFC Bank: Rs 450.00 debited from A/C XX4129 on 15-Nov-2026 to VPA zomato@hdfcbank...",
            "risk_score": 12,
            "risk_category": "LOW",
            "input_details": json.dumps({
                "message_text": "HDFC Bank: Rs 450.00 debited from A/C XX4129 on 15-Nov-2026 to VPA zomato@hdfcbank (UPI Ref no 987654123012). Available Bal: Rs 45,210.00. Call 18002586161 if not you."
            }),
            "detected_indicators": json.dumps([]),
            "ml_confidence": 0.0084,
            "explanation": "This message exhibits legitimate bank transaction alert patterns. It contains a standard masking convention (XX4129), standard reference number, toll-free dispute helpline, and contains no manipulative urgency, links, or credential requests.",
            "safety_recommendations": json.dumps([
                "Standard banking alert. No action required unless this transaction was unrecognized by you."
            ]),
            "created_at": now - timedelta(hours=14)
        },
        {
            "category": "TRANSACTION_ANOMALY",
            "input_summary": "Rapid 3-part account velocity drain at 2:41 AM totaling Rs 94,998.00",
            "risk_score": 95,
            "risk_category": "HIGH",
            "input_details": json.dumps({
                "transaction_ids": ["UPI1022", "UPI1023", "UPI1024"],
                "total_drain": 94998.0
            }),
            "detected_indicators": json.dumps([
                {"code": "RAPID_TRANSACTION_BURST", "title": "High Velocity Burst (3 transactions / hr)", "severity": "HIGH", "description": "Observed 3 transactions in a short rolling window, indicative of rapid account draining."},
                {"code": "OFF_HOURS_HIGH_VALUE", "title": "High-Value Late Night Transaction", "severity": "MEDIUM", "description": "Substantial debit occurred during uncustomary hours (1:00 AM - 5:00 AM)."},
                {"code": "ML_OUTLIER_DETECTED", "title": "Machine Learning Anomaly Pattern", "severity": "HIGH", "description": "Multi-dimensional anomaly identified by Isolation Forest behavioral model."}
            ]),
            "ml_confidence": 0.95,
            "explanation": "Flagged as HIGH RISK Anomaly (Score 95/100). The transaction sequence exhibits multiple critical indicators: 3 rapid high-value debits occurred between 2:41 AM and 2:53 AM to unfamiliar VPAs (fastcash.winner77@paytm, lottery.refund.claim@ybl), representing a drastic statistical deviation from historical daytime spending.",
            "safety_recommendations": json.dumps([
                "Immediately freeze UPI services through your mobile banking app or SMS.",
                "Call the National Cyber Crime Helpline at 1930 within the golden hour to freeze funds.",
                "Dispute the transactions with your bank using the UPI reference numbers."
            ]),
            "created_at": now - timedelta(hours=20)
        }
    ]

    for item in demo_analyses_data:
        analysis = FraudAnalysis(
            user_id=demo_user.id,
            category=item["category"],
            input_summary=item["input_summary"],
            input_details=item["input_details"],
            risk_score=item["risk_score"],
            risk_category=item["risk_category"],
            detected_indicators=item["detected_indicators"],
            ml_confidence=item["ml_confidence"],
            explanation=item["explanation"],
            safety_recommendations=item["safety_recommendations"],
            is_demo=True,
            created_at=item["created_at"]
        )
        db.add(analysis)

    # 3. Add demo fraud alerts
    alerts_data = [
        {
            "title": "Critical Alert: High-Risk Collect Request Detected",
            "description": "A simulated UPI collect request for Rs 4,999 from cashback.rewards@okhdfcbank was identified attempting PIN deception.",
            "risk_category": "HIGH",
            "created_at": now - timedelta(hours=2)
        },
        {
            "title": "Phishing Alert: Power Disconnection SMS Blocked",
            "description": "Urgent electricity bill SMS with suspicious link was flagged as phishing with 99.4% ML confidence.",
            "risk_category": "HIGH",
            "created_at": now - timedelta(hours=5)
        },
        {
            "title": "Anomaly Alert: Rapid Late-Night Transactions",
            "description": "Behavioral detection identified Rs 94,998 drained across 3 transactions at 2:41 AM.",
            "risk_category": "HIGH",
            "created_at": now - timedelta(hours=20)
        }
    ]

    for a in alerts_data:
        alert = FraudAlert(
            user_id=demo_user.id,
            title=a["title"],
            description=a["description"],
            risk_category=a["risk_category"],
            is_read=False,
            created_at=a["created_at"]
        )
        db.add(alert)

    # 4. Add demo transaction records (sample normal + anomalies)
    tx_samples = [
        ("UPI1001", "2026-11-14 10:15:00", 350.0, "DEBIT", "zomato@hdfcbank", "Lunch delivery", "SUCCESS", 10, "LOW", "[]"),
        ("UPI1002", "2026-11-14 13:40:00", 1200.0, "DEBIT", "blinkit@kotak", "Weekly groceries", "SUCCESS", 12, "LOW", "[]"),
        ("UPI1003", "2026-11-14 19:22:00", 180.0, "DEBIT", "priya.patel@okhdfcbank", "Shared cab fare", "SUCCESS", 8, "LOW", "[]"),
        ("UPI1004", "2026-11-15 02:41:10", 19999.0, "DEBIT", "fastcash.winner77@paytm", "UPI Collect Approval", "SUCCESS", 92, "HIGH", '["Isolation Forest Outlier", "Late Night (1-5 AM)", "High-Risk Merchant Category"]'),
        ("UPI1005", "2026-11-15 02:45:30", 25000.0, "DEBIT", "crypto.exchange.p2p@okaxis", "Express Transfer P2P", "SUCCESS", 94, "HIGH", '["Rapid Velocity (2 in 1hr)", "Late Night (1-5 AM)", "High Statistical Deviation"]'),
        ("UPI1006", "2026-11-15 02:49:15", 49999.0, "DEBIT", "lottery.refund.claim@ybl", "Authorization PIN entered", "SUCCESS", 98, "HIGH", '["Rapid Velocity (3 in 1hr)", "Late Night (1-5 AM)", "High-Risk Merchant Category", "High Statistical Deviation"]'),
        ("UPI1007", "2026-11-15 11:30:00", 65.0, "DEBIT", "motherdairy@paytm", "Daily Milk", "SUCCESS", 5, "LOW", "[]"),
    ]

    for tx in tx_samples:
        rec = TransactionRecord(
            user_id=demo_user.id,
            transaction_id=tx[0],
            timestamp=tx[1],
            amount=tx[2],
            transaction_type=tx[3],
            recipient_vpa=tx[4],
            description=tx[5],
            status=tx[6],
            risk_score=tx[7],
            risk_category=tx[8],
            anomaly_flags=tx[9]
        )
        db.add(rec)

    db.commit()
    print("Initial showcase dataset successfully seeded.")
    return demo_user

def reset_demo_data(db: Session, user: User):
    """
    Clears current analyses and re-seeds fresh simulated demo data.
    """
    db.query(FraudAnalysis).filter(FraudAnalysis.user_id == user.id).delete()
    db.query(FraudAlert).filter(FraudAlert.user_id == user.id).delete()
    db.query(TransactionRecord).filter(TransactionRecord.user_id == user.id).delete()
    db.commit()
    seed_demo_data(db)
