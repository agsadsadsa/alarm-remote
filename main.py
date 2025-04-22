import asyncio
import os
import websockets

clients = {}


async def handler(websocket):
    try:
        nickname, group, role = "", "", ""
        async for message in websocket:
            if message.startswith("REGISTER::"):
                _, nickname, group, role = message.split("::")
                print(f"[连接] {nickname} 加入 {group}")
                clients[websocket] = {"nickname": nickname, "group": group, "role": role}
                await broadcast_user_list()
            elif message.startswith("GROUP_CALL::"):
                _, sender, sender_group, sender_role = message.split("::")
                for ws, info in clients.items():
                    if ws != websocket and sender_group in info["group"].split(","):
                        await ws.send(f"GROUP_CALL::{sender}::{sender_group}::{sender_role}")
            elif message.startswith("KICK::"):
                _, sender, target = message.split("::")
                for ws, info in list(clients.items()):
                    if info["nickname"] == target:
                        await ws.send("KICKED")
                        await ws.close()
                        del clients[ws]
                        await broadcast_user_list()
    except:
        pass
    finally:
        if websocket in clients:
            print(f"[断开] {clients[websocket]['nickname']} 离开")
            del clients[websocket]
            await broadcast_user_list()

async def broadcast_user_list():
    user_list = ",".join(info["nickname"] for info in clients.values())
    for ws in clients:
        if ws.open:
            await ws.send(f"USERS::{user_list}")

async def main():
    port = int(os.getenv("PORT", 10000))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"服务器已启动，监听端口 {port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
