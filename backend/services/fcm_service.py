import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)

class FCMService:
    _initialized = False

    def __init__(self):
        if not FCMService._initialized:
            self._setup()

    def _setup(self):
        """Initialize Firebase Admin SDK."""
        key_path = os.path.join(os.getcwd(), "serviceAccountKey.json")
        if not os.path.exists(key_path):
            logger.warning(f"FCM Service: serviceAccountKey.json not found at {key_path}. Push notifications disabled.")
            return

        try:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            FCMService._initialized = True
            logger.info("FCM Service: Firebase Admin SDK initialized successfully.")
        except Exception as e:
            logger.error(f"FCM Service: Failed to initialize Firebase Admin SDK: {e}")

    async def send_push_notification(
        self, 
        token: str, 
        title: str, 
        body: str, 
        data: Optional[dict] = None
    ) -> bool:
        """Send a push notification to a specific device token."""
        if not FCMService._initialized:
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                android=messaging.AndroidConfig(
                    priority="high",
                ),
                data=data or {},
                token=token,
            )
            response = messaging.send(message)
            logger.info(f"FCM Service: Successfully sent message: {response}")
            return True
        except Exception as e:
            logger.error(f"FCM Service: Error sending FCM message: {e}")
            return False

fcm_service = FCMService()
