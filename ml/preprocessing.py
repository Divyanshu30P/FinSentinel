import re
import string

def preprocess_text(text: str) -> str:
    """
    Standardize financial text by replacing dynamic entities
    (URLs, phones, VPAs, amounts, account numbers) with semantic tokens.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # Normalize URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.[-\w.]+|[\w-]+\.(?:top|xyz|in|site|club|net|info|vip|online|org|com)(?:/[^\s]*)?'
    text = re.sub(url_pattern, ' <URL> ', text)

    # Normalize UPI VPAs (e.g. name@okaxis, xyz@paytm)
    vpa_pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
    text = re.sub(vpa_pattern, ' <VPA> ', text)

    # Normalize phone numbers (Indian mobile formats: +91, 10 digits)
    phone_pattern = r'(\+91[\-\s]?)?[6-9]\d{9}|\b\d{5}\s\d{5}\b'
    text = re.sub(phone_pattern, ' <PHONE> ', text)

    # Normalize currency amounts (e.g. Rs 500, Rs. 1,000, INR 5000)
    amount_pattern = r'(?:rs\.?|inr|₹)\s*[\d,]+(?:\.\d{1,2})?'
    text = re.sub(amount_pattern, ' <AMOUNT> ', text)

    # Normalize masked account numbers (XX1234, A/C 1234)
    acct_pattern = r'\b(?:a/c|acct|acc)\s*(?:no\.?)?\s*x*\d{4}\b'
    text = re.sub(acct_pattern, ' <ACCT> ', text)

    # Normalize OTP numbers
    otp_pattern = r'\b\d{4,6}\b'
    # Only replace if preceded by word otp or code
    text = re.sub(r'(otp|code|pin)\s*:?\s*(\d{4,6})', r'\1 <CODE>', text)

    # Remove generic punctuation except angle brackets for tokens
    cleaned = ""
    for ch in text:
        if ch in string.punctuation and ch not in '<>':
            cleaned += ' '
        else:
            cleaned += ch

    # Collapse multiple whitespaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
