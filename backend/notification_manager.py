from typing import List, Optional
import json
import logging

from websocket_manager import manager
from database import SessionLocal
from models import User
from services.fcm_service import fcm_service

logger = logging.getLogger(__name__)

class NotificationManager:
    @staticmethod
    async def send_notification(
        user_id: int,
        type: str,
        payload_data: dict
    ):
        """
        Sends a real-time notification via WebSocket and Push (FCM).
        """
        # 1. Prepare WebSocket payload
        ws_payload = {
            "type": type,
            **payload_data
        }

        # 2. Try WebSocket delivery (for foreground app)
        await manager.send_personal_message(ws_payload, user_id)

        # 3. Try Push delivery (for background/terminated app)
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                title, body = NotificationManager._get_notif_content(user, type, payload_data)
                
                # Try direct APNs first if we have the token
                apns_success = False
                if user.apns_token:
                    apns_success = await fcm_service.send_apns_push(
                        apns_token=user.apns_token,
                        title=title,
                        body=body,
                        data={"type": type, "payload": json.dumps(payload_data)}
                    )
                
                # If APNs failed (or we only have FCM token), try FCM
                if not apns_success and user.fcm_token:
                    await fcm_service.send_push_notification(
                        token=user.fcm_token,
                        title=title,
                        body=body,
                        data={"type": type, "payload": json.dumps(payload_data)}
                    )
        except Exception as e:
            logger.error(f"NotificationManager: Failed to send Push for user {user_id}: {e}")
        finally:
            db.close()

    @staticmethod
    def _get_notif_content(user, type: str, data: dict) -> tuple:
        """Helper to generate localized text for notifications."""
        lang = user.lang or "ru"
        
        if type == "new_order":
            if lang == "ru":
                return "Новый заказ!", f"Появился заказ: {data.get('subcategory_name_ru', 'Детали в приложении')}"
            else:
                return "Yangi buyurtma!", f"Buyurtma bor: {data.get('subcategory_name_uz', 'Batafsil ilovada')}"
                
        if type == "order_accepted":
            is_company = str(data.get('is_company', 'False')).lower() == 'true'
            if is_company:
                if lang == "ru":
                    return "Новый отклик!", f"Специалист {data.get('master_name', '')} откликнулся на вашу вакансию!"
                else:
                    return "Yangi javob!", f"Mutaxassis {data.get('master_name', '')} sizning vakansiyangizga javob berdi!"
            else:
                if lang == "ru":
                    return "Заказ принят", f"Мастер {data.get('master_name', '')} принял ваш заказ"
                else:
                    return "Buyurtma qabul qilindi", f"Usta {data.get('master_name', '')} buyurtmangizni qabul qildi"
                
        if type == "chat_message":
            return f"{data.get('sender_name', 'Сообщение')}", data.get("text", "Новое сообщение")
            
        if type == "order_completed":
            if lang == "ru":
                return "Заказ завершен", "Ваш заказ успешно выполнен"
            else:
                return "Buyurtma yakunlandi", "Buyurtmangiz muvaffaqiyatli yakunlandi"

        if type == "job_application":
            employer_name = data.get("employer_name", "")
            if lang == "ru":
                return "Новая заявка на работу!", f"{employer_name} оставил заявку на работу для вас"
            else:
                return "Yangi ish arizasi!", f"{employer_name} siz uchun ish arizasi qoldirdi"

        if type == "job_application_status":
            master_name = data.get("master_name", "")
            status_text = data.get(f"status_text_{'ru' if lang == 'ru' else 'uz'}", data.get("status", ""))
            if lang == "ru":
                return "Статус заявки обновлен", f"Мастер {master_name}: заявка {status_text}"
            else:
                return "Ariza holati yangilandi", f"Usta {master_name}: ariza {status_text}"

        return "Yaqin", "Новое уведомление"

notification_manager = NotificationManager()

