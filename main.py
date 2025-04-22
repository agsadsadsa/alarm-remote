import asyncio
import websockets
from collections import defaultdict

connected_users = dict()  # websocket: {"name": str, "groups": set}
admin_list = {"admin1", "superuser"}  # 管理员昵称列表

async def notify_user_list():
    user_names = [info["name"] for info in connected_users.values()]
    msg = "USERS::" + ",".join(user_names)
    for ws in connected_users:
        await ws.send(msg)

async def handler(websocket):
    try:
        async for message in websocket:
            if message.startswith("REGISTER::"):
                _, name, group_str = message.split("::", 2)
                groups = set(g.strip() for g in group_str.split(",") if g.strip())
                connected_users[websocket] = {"name": name, "groups": groups}
                await notify_user_list()

            elif message.startswith("GROUP_CALL::"):
                sender = connected_users.get(websocket, {}).get("name", "未知")
                sender_groups = connected_users.get(websocket, {}).get("groups", set())
                for ws, info in connected_users.items():
                    if ws != websocket and sender_groups & info["groups"]:
                        await ws.send(f"GROUP_CALL::{sender}")

            elif message.startswith("KICK::"):
                _, admin_name, target_name = message.split("::", 2)
                if admin_name in admin_list:
                    kicked_ws = None
                    for ws, info in connected_users.items():
                        if info["name"] == target_name:
                            kicked_ws = ws
                            break
                    if kicked_ws:
                        await kicked_ws.send("KICKED")
                        await kicked_ws.close()
                        print(f"[管理员] {admin_name} 移除了 {target_name}")
                else:
                    await websocket.send("[系统] 没有管理员权限")

    except websockets.ConnectionClosed:
        pass
    finally:
        if websocket in connected_users:
            del connected_users[websocket]
            await notify_user_list()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("服务器已启动，端口 10000")
        await asyncio.Future()
