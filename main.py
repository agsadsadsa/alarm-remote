from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from manager import connection_manager
from models import UserMessage
import json
import os
import uvicorn

app = FastAPI()

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await connection_manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await connection_manager.handle_message(username, message)
    except WebSocketDisconnect:
        await connection_manager.disconnect(username)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
