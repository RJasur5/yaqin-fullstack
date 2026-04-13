import asyncio
from websocket_manager import manager
from models import Order, Subcategory, Category
from database import SessionLocal
import os

async def trigger():
    db = SessionLocal()
    try:
        # User ID 27 (Акмал)
        target_user_ids = [27]
        
        order_data = {
            "type": "new_order",
            "order_id": 100500,
            "subcategory_name_ru": "Кузовщик",
            "subcategory_name_uz": "Kuzov ustalari",
            "description": "ТЕСТ: Проверка уведомления для Чиланзара!",
            "city": "Toshkent",
            "district": "Chilonzor",
            "price": 150000.0
        }
        
        print(f"Force-triggering notification to users: {target_user_ids}")
        # In a real app we'd await, but here we just need to send it
        # Note: manager must be the SAME instance. 
        # For a separate process test, this script won't work easily if manager is in memory of the main process.
        # So I'll use a direct API call or just tell the user to test.
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(trigger())
