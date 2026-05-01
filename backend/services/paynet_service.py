import base64
from typing import Dict, Any, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)

class PaynetService:
    def __init__(self):
        self.login = settings.PAYNET_LOGIN
        self.password = settings.PAYNET_PASSWORD

    def verify_auth(self, auth_header: Optional[str]) -> bool:
        if not auth_header or not auth_header.startswith("Basic "):
            return False

        try:
            encoded_credentials = auth_header.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            login, password = decoded_credentials.split(":", 1)

            if login == self.login and password == self.password:
                return True
            return False
        except Exception as e:
            logger.error(f"Paynet Auth Error: {e}")
            return False

paynet_service = PaynetService()
