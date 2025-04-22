import asyncio
import websockets
import json

clients = {}

async def notify_users():
    users = [user["nickname"] for user in clients.values()]
    message = f"USERS::{','.join(users)}"
    await asyncio.gather(*[ws.send(message) for ws in clients])

async def handler(websocket):
    try:
        async for message in websocket:
            if message.startswith("REGISTER::"):
                _, nickname, group, role = message.split("::")
                clients[websocket] = {"nickname": nickname, "group": group, "role": role}
                await notify_users()

            elif message.startswith("GROUP_CALL::"):
                _, nickname, group, role = message.split("::")
                for ws, info in clients.items():
                    if ws != websocket:
                        if role == "admin" or group in info["group"].split(","):
                            await ws.send(f"GROUP_CALL::{nickname}::{group}::{role}")

            elif message.startswith("KICK::"):
                _, sender, target_nick = message.split("::")
                for ws, info in list(clients.items()):
                    if info["nickname"] == target_nick:
                        try:
                            await ws.send("KICKED")
                        except:
                            pass
                        await ws.close()
                        del clients[ws]
                        await notify_users()
                        break

    except websockets.ConnectionClosed:
        pass
    finally:
        if websocket in clients:
            del clients[websocket]
            await notify_users()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("服务器已启动，监听端口 8000...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
