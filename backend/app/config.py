import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "UPI Shield - Financial Fraud Detection Platform"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "upi-shield-secure-secret-key-artha-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./upi_shield.db")
    
    # Gemini API Key (Optional)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Upload Configurations
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    
    # Demo User Credentials
    DEMO_USER_EMAIL: str = "demo@upishield.local"
    DEMO_USER_PASSWORD: str = "DemoShield@2026"
    DEMO_USER_NAME: str = "Hackathon Judge"

settings = Settings()
