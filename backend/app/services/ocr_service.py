import io
import shutil
from typing import Dict, Any, Optional
from PIL import Image

class OCRService:
    """
    OCR screenshot extraction service.
    Processes uploaded screenshots with format & size validation.
    Detects Tesseract binary presence and provides safe fallback presets when binary is absent.
    """

    SAMPLE_PRESETS = {
        "electricity": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210 or update now: http://power-bill-disconnection-alert.site/pay",
        "kyc": "Dear SBI User, your YONO SBI account has been blocked due to incomplete KYC. Please click here http://sbi-kyc-verify-portal.in/update to update your PAN and Aadhaar immediately to avoid permanent deactivation.",
        "collect": "Merchant Support sent you a collect request of Rs 4,999.00. Note: Enter UPI PIN to claim your Diwali cashback reward into your bank account."
    }

    @classmethod
    def is_tesseract_available(cls) -> bool:
        return shutil.which("tesseract") is not None

    @classmethod
    def extract_text_from_bytes(cls, image_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        # Validate format
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()
            image = Image.open(io.BytesIO(image_bytes))  # reopen after verify
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid or corrupted image format: {str(e)}",
                "extracted_text": "",
                "is_tesseract_installed": cls.is_tesseract_available()
            }

        # Check if tesseract binary is available
        if not cls.is_tesseract_available():
            # Graceful fallback: Inform user and provide matched preset text
            lower_name = filename.lower()
            preset_text = cls.SAMPLE_PRESETS["collect"]
            preset_name = "Simulated UPI Collect Screenshot"
            if "elect" in lower_name or "bill" in lower_name:
                preset_text = cls.SAMPLE_PRESETS["electricity"]
                preset_name = "Simulated Electricity Scam SMS Screenshot"
            elif "kyc" in lower_name or "bank" in lower_name or "sbi" in lower_name:
                preset_text = cls.SAMPLE_PRESETS["kyc"]
                preset_name = "Simulated Bank KYC Phishing Screenshot"

            return {
                "success": True,
                "extracted_text": preset_text,
                "is_tesseract_installed": False,
                "notice": "Tesseract OCR binary not detected on Windows host. Extracted preview populated via simulated screenshot preset. You can review and edit this text before scanning."
            }

        # Tesseract is available - run real OCR
        try:
            import pytesseract
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
            extracted = pytesseract.image_to_string(image)
            cleaned = extracted.strip()
            if not cleaned:
                return {
                    "success": False,
                    "error": "No readable text could be identified in the screenshot. Please check image clarity or type text manually.",
                    "extracted_text": "",
                    "is_tesseract_installed": True
                }
            return {
                "success": True,
                "extracted_text": cleaned,
                "is_tesseract_installed": True,
                "notice": "Text successfully extracted from screenshot using Tesseract OCR."
            }
        except Exception as err:
            return {
                "success": False,
                "error": f"OCR processing encountered an error: {str(err)}",
                "extracted_text": "",
                "is_tesseract_installed": True
            }
