from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Maps user_id -> List of active WebSockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        print(f"User {user_id} connected. Active connections: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            print(f"User {user_id} disconnected.")

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")

    async def broadcast_new_order(self, master_user_ids: List[int], order_data: dict):
        for user_id in master_user_ids:
            await self.send_personal_message(order_data, user_id)

    def get_active_users_count(self) -> int:
        # Filter out dead sockets in real-time
        active_count = 0
        to_remove_users = []
        
        for user_id, connections in self.active_connections.items():
            # Check if at least one socket is actually connected (client_state 1 = CONNECTED)
            # We use name check to be safe across different versions
            still_alive = [c for c in connections if hasattr(c, 'client_state') and c.client_state.name == 'CONNECTED']
            if still_alive:
                active_count += 1
                self.active_connections[user_id] = still_alive
            else:
                to_remove_users.append(user_id)
        
        for uid in to_remove_users:
            if uid in self.active_connections:
                del self.active_connections[uid]
                
        return active_count

manager = ConnectionManager()
