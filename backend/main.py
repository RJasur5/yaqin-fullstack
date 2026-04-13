from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time
from typing import Dict, List

from database import engine, Base
from routers import auth, masters, categories, favorites, orders, clients, admin, app_reviews

from websocket_manager import manager
from logging_config import setup_logging
import logging

# Setup professional logging
setup_logging()

# Create tables (back to auto-create for safety/troubleshooting)
Base.metadata.create_all(bind=engine)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="Yaqin API",
    description="API for Yaqin Services Marketplace App",
    version="1.0.0",
)

# --- DIAGNOSTIC MIDDLEWARE ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    # "Shout" in console about every request
    logging.info(f"==> REQUEST: {method} {path} from {request.client.host if request.client else 'unknown'}")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logging.info(f"<== RESPONSE: {response.status_code} (took {process_time:.2f}ms)")
    
    return response

# --- DEBUG ROUTES ---
@app.get("/api/test-notify/{user_id}")
async def test_notify(user_id: int):
    test_data = {
        "type": "new_order",
        "order_id": 100500,
        "subcategory_id": 1,
        "subcategory_name_ru": "Кузовщик",
        "subcategory_name_uz": "Kuzov ustalari",
        "description": "ТЕСТ: Полная покраска и вытяжка. Срочно! (Уведомление Мини-Окно)",
        "city": "Toshkent",
        "district": "Chilonzor",
        "price": 1500000.0
    }
    await manager.broadcast_new_order([user_id], test_data)
    return {"status": "sent", "user_id": user_id}

@app.get("/api/active-clients")
async def active_clients():
    return {"active_user_ids": list(manager.active_connections.keys())}

# --- END DEBUG ROUTES ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(masters.router)
app.include_router(categories.router)
app.include_router(favorites.router)
app.include_router(orders.router)
app.include_router(clients.router)
app.include_router(admin.router)
app.include_router(app_reviews.router)

# WebSocket Endpoint
@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    logging.info(f"!!! WEBSOCKET CONNECTED: user_id={user_id}")
    
    try:
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        logging.info(f"!!! WEBSOCKET DISCONNECTED: user_id={user_id}")
        manager.disconnect(user_id, websocket)
    except Exception as e:
        logging.error(f"!!! WEBSOCKET ERROR: user_id={user_id}, error={e}")
        manager.disconnect(user_id, websocket)


@app.get("/")
def root():
    return {
        "name": "Yaqin API",
        "version": "1.0.0",
        "status": "running",
        "ws_endpoint": "/ws/notifications/{user_id}",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}
