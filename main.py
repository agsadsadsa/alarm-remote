import asyncio
import websockets
import os
import logging

logging.basicConfig(level=logging.INFO)

PORT = int(os.environ.get("PORT", 10000))
connected_users = {}  # {websocket: nickname}

async def broadcast_users():
    users = ",".join(connected_users.values())
    message = f"USERS::{users}"
    await asyncio.gather(*[ws.send(message) for ws in connected_users])

async def broadcast_message(msg):
    await asyncio.gather(*[ws.send(msg) for ws in connected_users])

async def handler(websocket):
    try:
        nickname = await websocket.recv()
        connected_users[websocket] = nickname
        logging.info(f"{nickname} connected.")
        await broadcast_users()

        async for message in websocket:
            if message.startswith("CALL::"):
                await broadcast_message(message)
    except Exception as e:
        logging.warning(f"Error: {e}")
    finally:
        if websocket in connected_users:
            logging.info(f"{connected_users[websocket]} disconnected.")
            del connected_users[websocket]
            await broadcast_users()

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        logging.info(f"Server running on port {PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
