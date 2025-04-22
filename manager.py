from fastapi import WebSocket
from typing import Dict, List
from models import UserMessage

class ConnectionManager:
    def __init__(self):
        self.active_users: Dict[str, WebSocket] = {}
        self.groups: Dict[str, List[str]] = {}  # group_name -> usernames
        self.admins: List[str] = ["admin"]

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_users[username] = websocket
        await self.broadcast_user_list()

    async def disconnect(self, username: str):
        self.active_users.pop(username, None)
        await self.broadcast_user_list()

    async def broadcast_user_list(self):
        user_list = list(self.active_users.keys())
        for ws in self.active_users.values():
            await ws.send_json({"type": "user_list", "users": user_list})

    async def handle_message(self, sender: str, message: UserMessage):
        if message.type == "call":
            for target in self.groups.get(message.group, []):
                if target != sender and target in self.active_users:
                    await self.active_users[target].send_json({
                        "type": "call",
                        "from": sender,
                        "group": message.group
                    })
        elif message.type == "join_group":
            self.groups.setdefault(message.group, []).append(sender)
        elif message.type == "kick_user":
            if sender in self.admins and message.target in self.active_users:
                await self.active_users[message.target].close()
                await self.disconnect(message.target)

connection_manager = ConnectionManager()
