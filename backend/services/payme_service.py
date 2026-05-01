import base64
import os
from typing import Dict, Any, Optional
from config import settings

class PaymeService:
    def __init__(self):
        self.merchant_id = settings.PAYME_ID
        self.key = settings.PAYME_TEST_KEY if settings.PAYME_USE_TEST else settings.PAYME_KEY
        self.base_url = "https://checkout.paycom.uz"
        if settings.PAYME_USE_TEST:
             self.base_url = "https://test.paycom.uz"

    def generate_payment_url(self, amount: float, account: Dict[str, Any], return_url: Optional[str] = None) -> str:
        """
        Generates a checkout URL for Payme.
        amount is in sum (will be converted to tiyin).
        account is a dict like {'user_id': 123, 'plan': 'month'}
        """
        # Payme expects amount in tiyins (1 sum = 100 tiyins)
        amount_tiyin = int(amount * 100)
        
        # Create params string for base64
        # Format: m={merchant_id};ac.{key1}={val1};ac.{key2}={val2};a={amount}
        params = f"m={self.merchant_id};a={amount_tiyin}"
        for k, v in account.items():
            params += f";ac.{k}={v}"
            
        if return_url:
            params += f";c={return_url}"
            
        encoded_params = base64.b64encode(params.encode()).decode()
        return f"{self.base_url}/{encoded_params}"

    def verify_auth(self, auth_header: str) -> bool:
        """
        Verifies the Basic Auth header sent by Payme.
        Payme sends: Basic base64(Paycom:key)
        """
        if not auth_header or not auth_header.startswith("Basic "):
            return False
            
        try:
            encoded = auth_header.split(" ")[1]
            decoded = base64.b64decode(encoded).decode()
            
            # Format should be Paycom:KEY
            expected = f"Paycom:{self.key}"
            return decoded == expected
        except Exception:
            return False

payme_service = PaymeService()
