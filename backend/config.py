import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///findix.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "findix-secret-key-2026-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    TOKEN_EXPIRE_DAYS: int = int(os.getenv("TOKEN_EXPIRE_DAYS", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Production Info
    PROD_DOMAIN: str = os.getenv("PROD_DOMAIN", "yaqingo.uz")
    PROD_IP: str = os.getenv("PROD_IP", "95.182.118.245")
    
    # Click Payment
    CLICK_SERVICE_ID: str = os.getenv("CLICK_SERVICE_ID", "")
    CLICK_MERCHANT_ID: str = os.getenv("CLICK_MERCHANT_ID", "")
    CLICK_SECRET_KEY: str = os.getenv("CLICK_SECRET_KEY", "")

    # Payme Payment
    PAYME_ID: str = os.getenv("PAYME_ID", "")
    PAYME_KEY: str = os.getenv("PAYME_KEY", "")
    PAYME_TEST_KEY: str = os.getenv("PAYME_TEST_KEY", "")
    PAYME_USE_TEST: bool = os.getenv("PAYME_USE_TEST", "true").lower() == "true"

    # Paynet Payment
    PAYNET_LOGIN: str = os.getenv("PAYNET_LOGIN", "yaqingo")
    PAYNET_PASSWORD: str = os.getenv("PAYNET_PASSWORD", "ZxCvBn")
    PAYNET_SERVICE_ID: str = os.getenv("PAYNET_SERVICE_ID", "155")

    class Config:
        env_file = ".env"
        extra = "ignore"

# Global settings instance
settings = Settings()
