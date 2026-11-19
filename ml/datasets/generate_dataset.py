"""
FinSentinel - Comprehensive Dataset Generator for Financial Phishing & SMS Scam Detection
Combines real Indian banking SMS patterns, reported cybercrime templates (1930 helpline),
and legitimate financial communications.
"""

import pandas as pd
import random

# Real reported scam and phishing message templates (Label = 1)
PHISHING_TEMPLATES = [
    # Electricity Bill Scam
    "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at {phone} or update now: {url}",
    "URGENT: Your electricity supply will be disconnected today at 10 PM. Last month unpaid bill. Call electricity department officer at {phone} or install support app: {url}",
    "Dear Customer Your Electricity connection will be cut off tonight at 9:30 pm from electricity office. Immediately call power officer at {phone}",
    "URGENT NOTICE: Electricity disconnection scheduled for tonight due to pending bill Rs {amount}. Avoid disconnection by paying immediately through link: {url} or contact officer at {phone}",
    
    # Fake Bank KYC / Account Suspension
    "Dear SBI User, your YONO SBI account has been blocked due to incomplete KYC. Please click here {url} to update your PAN and Aadhaar immediately to avoid permanent deactivation.",
    "Dear HDFC Customer, your NetBanking access is suspended today due to KYC non-compliance. Update your KYC within 24 hours at {url} to restore services.",
    "Alert: ICICI Bank A/C {acct} blocked today. Kindly update your PAN card details to resume online transactions. Click to verify: {url}",
    "Your PNB Bank account will be closed within 12 hours. Please complete your biometric KYC update by visiting {url} immediately.",
    "Axis Bank Alert: Dear customer your savings account has been put on hold due to missing mandatory document. Verify identity now at {url}",
    "Dear customer, your bank account has been temporarily restricted. Submit your Aadhaar card and PAN card at {url} to reactivate your UPI services.",
    "Canara Bank: Your debit card is blocked. Download our official KYC apk file from {url} to unblock your card and continue UPI transactions.",
    "Bank Alert: Your account is scheduled for deactivation due to KYC lapse. Call bank manager at {phone} or visit secure portal: {url}",

    # Fake Rewards, Cashback & Lottery
    "Congratulations! You have received a cashback reward of Rs {amount} on PhonePe. Click here to claim your reward in bank account: {url}",
    "Paytm Reward: You have won Rs {amount} scratch card cashback! Enter your UPI PIN on the link {url} to credit reward instantly to your account.",
    "Google Pay Alert: A scratch card worth Rs {amount} is waiting for you. Claim your money now by clicking {url} and approving the collect request.",
    "Dear User, you have won Rs {amount} in lucky draw contest 2026. Send your UPI ID and approve request to claim cash prize now: {url}",
    "KBC Season 16 Lucky Winner: Congratulations, your mobile number has won Rs 25,00,000 cash. Contact KBC manager at WhatsApp {phone} to claim prize.",
    "Special Offer: Claim your pending GST refund of Rs {amount} directly to your bank account. Submit bank details and OTP at {url}",
    "Cred Club Reward: You have 15,400 unused reward points expiring tonight worth Rs {amount}. Redeem immediately as cash to your UPI VPA: {url}",

    # Fake Customer Support & APK Scam
    "Dear user, facing issues with your refund? Customer support helpline {phone}. Download AnyDesk / TeamViewer QuickSupport from {url} to resolve.",
    "Swiggy refund pending: We are unable to credit Rs {amount}. Please download customer care support tool {url} or share screen with our agent {phone}.",
    "Zomato Customer Care: For urgent resolution of failed order payment, call toll-free {phone} or open link {url} to initiate instant reversal.",
    "IRCTC refund failed: Your train ticket cancellation refund of Rs {amount} failed. Call railway refund executive at {phone} to receive refund via UPI.",
    "Amazon Support: Order delivery failed. Update address and pay re-delivery fee of Rs 5 using link {url} to avoid return of parcel.",
    "Courier Delivery Alert: Indian Post parcel tracking {phone} is held due to incomplete address. Pay verification fee Rs 10 at {url} to release shipment.",

    # Fake UPI Collect & PIN Scam
    "Dear Customer, you received a collect request of Rs {amount} from Merchant Support. Enter your UPI PIN to receive money in your account.",
    "OLX Buyer Alert: I have sent you an advance payment of Rs {amount} via PhonePe collect request. Kindly accept and enter PIN to verify payment.",
    "Money Transfer: Rs {amount} is ready to be credited to your account. Open your GPay app and enter UPI PIN to receive money into your bank.",
    "Army Officer Purchase: Sending Rs {amount} advance for your vehicle on OLX. Please scan this QR code or accept collect request and input PIN.",

    # Part-time Job & Crypto Scam
    "Work from Home Opportunity: Earn Rs 3,000 - 8,000 daily by simply reviewing Google Maps locations and YouTube videos. Contact HR on WhatsApp: {phone}",
    "Earn daily income from home! High commission part time task. No investment required. Contact our Telegram coordinator at {url} or {phone}",
    "Crypto Investment Alert: Guaranteed 200% return in 24 hours. Invest minimum Rs {amount} in Binance arbitrage. Join VIP group: {url}",
    "Dear Candidate, your resume was shortlisted for part time online evaluation. Daily payout Rs 5,000. Ping us on WhatsApp {phone}"
]

# Real legitimate banking & transactional message templates (Label = 0)
LEGITIMATE_TEMPLATES = [
    # UPI Debit Notification
    "Dear SBI UPI user, your A/C {acct} has been debited by Rs {amount} on {date} by UPI ref no {ref}. If not done by you, forward this SMS to 9223008333 to block UPI.",
    "HDFC Bank: Rs {amount} debited from A/C {acct} on {date} to VPA {vpa} (UPI Ref no {ref}). Available Bal: Rs {balance}. Call 18002586161 if not you.",
    "ICICI Bank: A/C {acct} debited for Rs {amount} on {date}. UPI: {ref}. Avail Bal: Rs {balance}. Report unauthorized transaction call 18001080.",
    "Axis Bank: Rs {amount} debited from A/C {acct} via UPI on {date} to {vpa}. Bal Rs {balance}. Dial 18001035577 to dispute.",
    "Kotak Bank: Rs {amount} debited from A/C {acct} on {date} for UPI/P2M/{ref}. Available balance is Rs {balance}.",

    # UPI Credit Notification
    "Dear Customer, your A/C {acct} has been credited by Rs {amount} on {date} by UPI/P2P/{vpa}. UPI Ref {ref}. Available balance: Rs {balance}.",
    "HDFC Bank: Rs {amount} credited to A/C {acct} on {date} through UPI from {vpa}. Total balance: Rs {balance}.",
    "ICICI Bank: Your A/C {acct} is credited with Rs {amount} on {date} via NEFT/UPI from employer. Avail Bal: Rs {balance}.",
    "State Bank of India: Rs {amount} credited to account {acct} on {date} by salary transfer. Clear balance Rs {balance}.",

    # Genuine OTP & Login alerts (Legitimate notices clearly say NEVER share)
    "{otp} is your secret OTP for transaction of Rs {amount} at Merchant Portal. NEVER share this OTP with anyone, bank staff will never ask for OTP.",
    "Use OTP {otp} to login to your HDFC Bank NetBanking. Valid for 3 mins. Do NOT share OTP or PIN with anyone, including bank employees.",
    "SBI: {otp} is your One Time Password for login to YONO. Valid for 10 minutes. Bank never calls asking for OTP or password.",
    "{otp} is your verification code for GPay registration. Do not share this code with anyone.",
    "Your PhonePe verification code is {otp}. Valid for 5 minutes. Never disclose this code to anyone for your account safety.",

    # Genuine Bills & Utility Receipts
    "Dear Consumer, payment of Rs {amount} for Electricity CA No {acct} received successfully on {date} via UPI. Receipt ref: {ref}. Thank you, BSES Rajdhani.",
    "Jio Prepaid: Recharge of Rs {amount} is successful for your mobile on {date}. Plan benefits: 1.5GB/day, Unlimited Calls. Validity: 28 days.",
    "Airtel: Thank you for paying your broadband bill of Rs {amount}. Transaction ID {ref}. Payment credited successfully.",
    "Swiggy: Your order #{acct} of Rs {amount} has been placed successfully and is being prepared. Track live in app.",
    "Zomato: Payment of Rs {amount} received for order #{acct}. Delivery executive assigned.",
    "Uber: Your receipt for trip on {date}. Amount charged: Rs {amount} via UPI. Thank you for riding with Uber.",
    "IRCTC: Booking confirmed for PNR {acct}. Train 12952, Class 3A. Total fare Rs {amount} debited from A/C {acct}."
]

def generate_synthetic_samples():
    urls = [
        "http://sbi-kyc-verify-portal.in/update",
        "https://power-bill-disconnection-alert.site/pay",
        "http://hdfc-netbanking-secure-login.xyz",
        "http://bit.ly/claim-phonepe-cashback",
        "http://tinyurl.com/electricity-bill-pay-officer",
        "https://anydesk-support-apk-download.net/app",
        "http://icici-pan-link-now.top/verify",
        "http://paytm-scratch-card-2026.club",
        "https://telegram.dog/quick_income_task_vip",
        "http://ngrok-free.app/yono-login-auth",
        "http://192.168.1.105:8080/collect-apk.apk",
        "http://fast-refund-desk-portal.info"
    ]
    
    phones = [
        "+91 98765 43210", "+91 87654 32109", "+91 76543 21098", "+91 91234 56789",
        "9988776655", "8877665544", "7766554433", "+91 94321 09876"
    ]

    vpas = [
        "rajesh.sharma@okaxis", "merchant.store@okhdfcbank", "swiggy@icici",
        "zomato@hdfcbank", "bses.bill@sbi", "airtel.pay@airtel", "rahul.gupta@paytm"
    ]

    dates = ["12-Nov-2026", "14-Nov-2026", "15-Nov-2026", "16-Nov-2026", "10-Oct-2026"]
    
    rows = []

    # Generate Phishing samples
    for i in range(350):
        tmpl = random.choice(PHISHING_TEMPLATES)
        msg = tmpl.format(
            phone=random.choice(phones),
            url=random.choice(urls),
            amount=random.choice(["2,450", "4,999", "10,000", "25,000", "5,500", "750", "15,000"]),
            acct=f"XX{random.randint(1000, 9999)}"
        )
        rows.append({"text": msg, "label": 1, "category": "phishing"})

    # Generate Legitimate samples
    for i in range(350):
        tmpl = random.choice(LEGITIMATE_TEMPLATES)
        msg = tmpl.format(
            amount=random.choice(["150.00", "340.50", "1,200.00", "4,500.00", "850.00", "14,200.00", "28,500.00", "45.00"]),
            acct=f"XX{random.randint(1000, 9999)}",
            date=random.choice(dates),
            ref=f"{random.randint(100000000000, 999999999999)}",
            vpa=random.choice(vpas),
            balance=f"{random.randint(5000, 150000):,}.00",
            otp=f"{random.randint(100000, 999999)}"
        )
        rows.append({"text": msg, "label": 0, "category": "legitimate"})

    random.shuffle(rows)
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate_synthetic_samples()
    output_path = "ml/datasets/sms_phishing_dataset.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Dataset successfully created with {len(df)} samples at {output_path}")
    print(df["label"].value_counts())
