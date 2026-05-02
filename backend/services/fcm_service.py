import firebase_admin
from firebase_admin import credentials, messaging
from typing import Optional
import os
import logging
import json
import time
import jwt
import httpx

logger = logging.getLogger(__name__)

class FCMService:
    _initialized = False
    _apns_key = None
    _apns_key_id = "XFX3836M5A"
    _apns_team_id = "CQCS55M636"
    _apns_bundle_id = "com.yaqin.findix"
    _apns_token = None
    _apns_token_expiry = 0

    def __init__(self):
        if not FCMService._initialized:
            self._setup()

    def _setup(self):
        """Initialize Firebase Admin SDK and APNs direct sending."""
        key_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
        if os.path.exists(key_path):
            try:
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
                logger.info("FCM Service: Firebase Admin SDK initialized.")
            except Exception as e:
                logger.error(f"FCM Service: Firebase init error: {e}")

        # Load APNs .p8 key for direct APNs sending
        p8_path = os.path.join(os.getcwd(), "AuthKey_XFX3836M5A.p8")
        if os.path.exists(p8_path):
            with open(p8_path, "r") as f:
                FCMService._apns_key = f.read()
            logger.info("FCM Service: APNs .p8 key loaded for direct push.")
        else:
            logger.warning(f"FCM Service: No APNs .p8 key at {p8_path}. Direct APNs disabled.")

        FCMService._initialized = True

    def _get_apns_token(self):
        """Generate or reuse a JWT token for APNs."""
        now = int(time.time())
        # Reuse token for 50 minutes (APNs tokens valid for 60 min)
        if FCMService._apns_token and now < FCMService._apns_token_expiry:
            return FCMService._apns_token

        headers = {
            "alg": "ES256",
            "kid": self._apns_key_id,
        }
        payload = {
            "iss": self._apns_team_id,
            "iat": now,
        }
        token = jwt.encode(payload, FCMService._apns_key, algorithm="ES256", headers=headers)
        FCMService._apns_token = token
        FCMService._apns_token_expiry = now + 3000  # 50 minutes
        return token

    async def _send_apns_direct(self, device_token: str, title: str, body: str, data: dict = None) -> bool:
        """Send push notification directly via APNs HTTP/2 API."""
        if not FCMService._apns_key:
            return False

        apns_jwt = self._get_apns_token()

        # Try sandbox first (for Xcode builds), then production
        for use_sandbox in [True, False]:
            if use_sandbox:
                url = f"https://api.sandbox.push.apple.com/3/device/{device_token}"
            else:
                url = f"https://api.push.apple.com/3/device/{device_token}"

            payload = {
                "aps": {
                    "alert": {"title": title, "body": body},
                    "sound": "default",
                    "badge": 1,
                },
            }
            if data:
                payload["data"] = data

            headers = {
                "authorization": f"bearer {apns_jwt}",
                "apns-topic": self._apns_bundle_id,
                "apns-push-type": "alert",
                "apns-priority": "10",
            }

            try:
                async with httpx.AsyncClient(http2=True) as client:
                    response = await client.post(url, json=payload, headers=headers, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"APNs direct push SUCCESS via {'sandbox' if use_sandbox else 'production'}")
                        return True
                    else:
                        resp_body = response.text
                        logger.warning(f"APNs {'sandbox' if use_sandbox else 'production'} failed ({response.status_code}): {resp_body}")
                        # If sandbox failed with BadDeviceToken, try production
                        if "BadDeviceToken" in resp_body:
                            continue
                        # If it's another error on sandbox, still try production
                        if use_sandbox:
                            continue
                        return False
            except Exception as e:
                logger.error(f"APNs direct push error ({'sandbox' if use_sandbox else 'production'}): {e}")
                if use_sandbox:
                    continue
                return False

        return False

    async def send_push_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """Send push notification. Tries direct APNs first, falls back to FCM."""
        if not FCMService._initialized:
            return False

        # For iOS tokens (APNs device tokens are hex strings), try direct APNs
        if FCMService._apns_key:
            # We store the APNs device token separately now
            # But we can also try with FCM token through Firebase
            pass

        # Try FCM (works for Android, may fail for iOS due to environment mismatch)
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(
                    headers={"apns-priority": "10"},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(title=title, body=body),
                            sound="default",
                            badge=1,
                        ),
                    ),
                ),
                data=data or {},
                token=token,
            )
            response = messaging.send(message)
            logger.info(f"FCM push SUCCESS: {response}")
            return True
        except Exception as e:
            logger.error(f"FCM push failed: {e}")

        return False

    async def send_apns_push(self, apns_token: str, title: str, body: str, data: dict = None) -> bool:
        """Send push directly via APNs using device token."""
        return await self._send_apns_direct(apns_token, title, body, data)

fcm_service = FCMService()
