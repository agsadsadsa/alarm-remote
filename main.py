from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

clients = {}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def notify_users():
    users = [info["nickname"] for info in clients.values()]
    message = f"USERS::{','.join(users)}"
    for ws in clients:
        await ws.send_text(message)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            if message.startswith("REGISTER::"):
                _, nickname, group, role = message.split("::")
                clients[websocket] = {"nickname": nickname, "group": group, "role": role}
                await notify_users()

            elif message.startswith("GROUP_CALL::"):
                _, nickname, group, role = message.split("::")
                for ws, info in clients.items():
                    if group in info["group"].split(","):
                        await ws.send_text(f"GROUP_CALL::{nickname}::{group}::{role}")

            elif message.startswith("KICK::"):
                _, sender, target_nick = message.split("::")
                to_kick = None
                for ws, info in clients.items():
                    if info["nickname"] == target_nick:
                        to_kick = ws
                        break
                if to_kick:
                    await to_kick.send_text("KICKED")
                    await to_kick.close()
                    del clients[to_kick]
                    await notify_users()
    except WebSocketDisconnect:
        if websocket in clients:
            del clients[websocket]
            await notify_users()
