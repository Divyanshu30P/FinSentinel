"""
FinSentinel - Sample Screenshot Image Generator
Creates realistic simulated screenshot images of:
1. Electricity bill disconnection phishing SMS
2. Bank KYC deactivation SMS
3. Fake UPI collect request screen
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_sample_images():
    os.makedirs("frontend/assets/samples", exist_ok=True)

    # 1. Electricity bill phishing screenshot
    img1 = Image.new("RGB", (600, 320), color="#1A1C23")
    d1 = ImageDraw.Draw(img1)
    d1.rectangle([(20, 20), (580, 70)], fill="#232733")
    d1.text((35, 35), "SMS: +91 98765 43210 (Electricity Dept)", fill="#5599FF")
    
    msg1 = (
        "Dear Consumer, your electricity power will be\n"
        "disconnected tonight at 9:30 PM from the\n"
        "electricity office because your previous month\n"
        "bill was not updated. Please immediately contact\n"
        "our electricity officer at 9876543210 or update:\n"
        "http://power-bill-disconnection-alert.site/pay"
    )
    d1.rectangle([(20, 90), (580, 290)], fill="#2D3242")
    d1.text((35, 110), msg1, fill="#F1F5F9")
    img1.save("frontend/assets/samples/sms_electricity_bill_scam.png")

    # 2. Bank KYC phishing screenshot
    img2 = Image.new("RGB", (600, 300), color="#1A1C23")
    d2 = ImageDraw.Draw(img2)
    d2.rectangle([(20, 20), (580, 70)], fill="#232733")
    d2.text((35, 35), "SMS: AX-SBINB (Alert)", fill="#35C99A")
    
    msg2 = (
        "Dear SBI User, your YONO SBI account has been\n"
        "blocked due to incomplete KYC. Please click here\n"
        "http://sbi-kyc-verify-portal.in/update to update\n"
        "your PAN and Aadhaar immediately to avoid\n"
        "permanent deactivation of UPI services."
    )
    d2.rectangle([(20, 90), (580, 270)], fill="#2D3242")
    d2.text((35, 110), msg2, fill="#F1F5F9")
    img2.save("frontend/assets/samples/sms_bank_kyc_phishing.png")

    # 3. UPI Collect Request screenshot
    img3 = Image.new("RGB", (600, 320), color="#111827")
    d3 = ImageDraw.Draw(img3)
    d3.rectangle([(20, 20), (580, 80)], fill="#1F2937")
    d3.text((35, 35), "UPI Money Collect Request", fill="#F4B942")
    d3.text((35, 55), "From: cashback.rewards@okhdfcbank", fill="#94A3B8")
    
    msg3 = (
        "Requested Amount: Rs. 4,999.00\n"
        "Description: Diwali Cashback Reward Claim\n\n"
        "Note: Tap Accept and enter your UPI PIN to\n"
        "credit reward into your bank account immediately."
    )
    d3.rectangle([(20, 100), (580, 290)], fill="#1E293B")
    d3.text((35, 120), msg3, fill="#F8FAFC")
    img3.save("frontend/assets/samples/upi_collect_request_scam.png")

    print("Sample screenshot images successfully created in frontend/assets/samples/")

if __name__ == "__main__":
    create_sample_images()
