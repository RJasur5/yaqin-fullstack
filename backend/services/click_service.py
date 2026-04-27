import hashlib
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class ClickService:
    def __init__(self):
        self.service_id = os.getenv("CLICK_SERVICE_ID")
        self.merchant_id = os.getenv("CLICK_MERCHANT_ID")
        self.secret_key = os.getenv("CLICK_SECRET_KEY")
        self.domain = os.getenv("PROD_DOMAIN", "yaqingo.uz")

    def generate_payment_url(self, amount: float, transaction_param: str) -> str:
        """
        Generates a redirect URL for Click payment.
        transaction_param is usually the user_id or subscription_id.
        """
        # Format: https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={transaction_param}
        url = (
            f"https://my.click.uz/services/pay"
            f"?service_id={self.service_id}"
            f"&merchant_id={self.merchant_id}"
            f"&amount={amount:.2f}"
            f"&transaction_param={transaction_param}"
        )
        return url

    def verify_signature(self, data: Dict[str, Any]) -> bool:
        """
        Bulletproof signature verification with detailed logging.
        """
        logger = logging.getLogger(__name__)
        try:
            click_trans_id = str(data.get("click_trans_id", ""))
            service_id = str(data.get("service_id", ""))
            merchant_trans_id = str(data.get("merchant_trans_id", ""))
            merchant_prepare_id = str(data.get("merchant_prepare_id", ""))
            amount = str(data.get("amount", ""))
            action = str(data.get("action", ""))
            error = str(data.get("error", "0"))
            sign_time = str(data.get("sign_time", ""))
            received_sign = str(data.get("sign_string") or data.get("sign") or "")

            # Action 0 Formula
            if action == "0":
                sign_string = f"{click_trans_id}{service_id}{self.secret_key}{merchant_trans_id}{amount}{action}{sign_time}"
            else:
                sign_string = f"{click_trans_id}{service_id}{self.secret_key}{merchant_trans_id}{merchant_prepare_id}{amount}{action}{sign_time}"
            
            calculated_sign = hashlib.md5(sign_string.encode()).hexdigest()
            
            if calculated_sign == received_sign:
                return True

            # Try alt with error
            if action == "0":
                alt_string = f"{click_trans_id}{service_id}{self.secret_key}{merchant_trans_id}{amount}{action}{error}{sign_time}"
            else:
                alt_string = f"{click_trans_id}{service_id}{self.secret_key}{merchant_trans_id}{merchant_prepare_id}{amount}{action}{error}{sign_time}"
            
            alt_sign = hashlib.md5(alt_string.encode()).hexdigest()
            if alt_sign == received_sign:
                return True

            logger.error(f"CLICK SIGN MISMATCH! Rec: {received_sign}, Calc: {calculated_sign}, String: {sign_string}")
            return False
            
        except Exception as e:
            logger.error(f"CLICK SIGN ERROR: {e}")
            return False

click_service = ClickService()
