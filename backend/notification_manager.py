from typing import List, Optional
import json

from websocket_manager import manager
from database import SessionLocal

class NotificationManager:
    @staticmethod
    async def send_notification(
        user_id: int,
        type: str,
        payload_data: dict
    ):
        """
        Sends a real-time notification via WebSocket.
        """
        # Prepare payload
        ws_payload = {
            "type": type,
            **payload_data
        }

        # Send if online
        await manager.send_personal_message(ws_payload, user_id)


notification_manager = NotificationManager()
