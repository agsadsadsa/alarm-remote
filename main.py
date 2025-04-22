import asyncio
import websockets
import json

# 在线用户字典：{ websocket: {"name": str, "groups": set(str)} }
connected_users = {}

async def notify_user_list():
    """广播在线用户列表"""
    users = [info["name"] for info in connected_users.values()]
    message = f"USERS::{','.join(users)}"
    await asyncio.gather(*[
        ws.send(message) for ws in connected_users
    ])

async def handler(websocket):
    try:
        # 等待客户端发送注册信息
        async for message in websocket:
            if message.startswith("REGISTER::"):
                _, name, group_str = message.split("::", 2)
                groups = set(g.strip() for g in group_str.split(",") if g.strip())
                connected_users[websocket] = {"name": name, "groups": groups}
                print(f"{name} 加入了，分组: {groups}")
                await notify_user_list()

            elif message.startswith("GROUP_CALL::"):
                sender = connected_users.get(websocket, {}).get("name", "未知")
                sender_groups = connected_users.get(websocket, {}).get("groups", set())
                if sender_groups:
                    for ws, info in connected_users.items():
                        if ws != websocket and sender_groups & info["groups"]:
                            await ws.send(f"GROUP_CALL::{sender}")
                print(f"{sender} 呼叫了分组 {sender_groups}")

    except websockets.ConnectionClosed:
        pass
    finally:
        if websocket in connected_users:
            print(f"{connected_users[websocket]['name']} 离线")
            del connected_users[websocket]
            await notify_user_list()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("服务端启动，监听端口 10000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
