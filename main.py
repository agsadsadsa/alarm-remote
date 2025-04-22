import asyncio
import websockets

clients = {}

async def notify_users():
    users = [info["nickname"] for info in clients.values()]
    message = f"USERS::{','.join(users)}"
    await asyncio.gather(*[ws.send(message) for ws in clients if ws.open])

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
                    if ws.open and group in info["group"].split(","):
                        await ws.send(f"GROUP_CALL::{nickname}::{group}::{role}")

            elif message.startswith("KICK::"):
                _, sender, target_nick = message.split("::")
                to_kick = None
                for ws, info in clients.items():
                    if info["nickname"] == target_nick:
                        to_kick = ws
                        break

                if to_kick:
                    try:
                        await to_kick.send("KICKED")
                        await to_kick.close()
                    except:
                        pass
                    finally:
                        if to_kick in clients:
                            del clients[to_kick]
                    await notify_users()

    except websockets.ConnectionClosed:
        pass
    finally:
        if websocket in clients:
            del clients[websocket]
            await notify_users()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("服务器已启动，监听端口 10000...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
