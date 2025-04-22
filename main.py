
import asyncio
import websockets

connected_users = {}  # websocket -> {'nickname': str, 'group': str}
user_lookup = {}      # nickname -> websocket

async def notify_group(group, sender_nick, message):
    for ws, info in connected_users.items():
        if info.get('group') == group and info.get('nickname') != sender_nick:
            await ws.send(message)

async def update_user_lists():
    users = ",".join(info['nickname'] for info in connected_users.values())
    for ws in connected_users:
        await ws.send("USERS::" + users)

async def handle_client(ws):
    try:
        async for message in ws:
            if message.startswith("REGISTER::"):
                _, nickname, group = message.split("::")
                connected_users[ws] = {'nickname': nickname, 'group': group}
                user_lookup[nickname] = ws
                await update_user_lists()

            elif message.startswith("GROUP_CALL::"):
                _, nickname = message.split("::")
                user_info = connected_users.get(ws)
                if user_info:
                    group = user_info['group']
                    await notify_group(group, nickname, f"GROUP_CALL::{nickname}")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if ws in connected_users:
            nickname = connected_users[ws]['nickname']
            user_lookup.pop(nickname, None)
            connected_users.pop(ws, None)
            await update_user_lists()

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("Server running at ws://0.0.0.0:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
