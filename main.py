
import asyncio
import websockets

connected_users = {}  # websocket -> {'nickname': str, 'group': str}
user_lookup = {}      # nickname -> websocket

async def notify_all(message):
    for ws in connected_users:
        await ws.send(message)

async def notify_user(nickname, message):
    ws = user_lookup.get(nickname)
    if ws:
        await ws.send(message)

async def notify_group(group, sender_nick, message):
    for ws, info in connected_users.items():
        if info.get('group') == group and info.get('nickname') != sender_nick:
            await ws.send(message)

async def update_user_lists():
    users = ",".join(info['nickname'] for info in connected_users.values())
    groups = set(info['group'] for info in connected_users.values())
    group_msg = "GROUPS::" + ",".join(groups)
    user_msg = "USERS::" + users
    for ws in connected_users:
        await ws.send(user_msg)
        await ws.send(group_msg)

async def handle_client(ws):
    try:
        async for message in ws:
            if message.startswith("NICK::"):
                nickname = message[6:]
                connected_users[ws] = {'nickname': nickname, 'group': '默认分组'}
                user_lookup[nickname] = ws
                await update_user_lists()

            elif message.startswith("JOIN_GROUP::"):
                _, nickname, group = message.split("::")
                if ws in connected_users:
                    connected_users[ws]['group'] = group
                await update_user_lists()

            elif message.startswith("CALL::"):
                nickname = message[6:]
                await notify_all(f"CALL::{nickname}")

            elif message.startswith("PRIVATE_CALL::"):
                _, sender, target = message.split("::")
                await notify_user(target, f"PRIVATE_CALL::{sender}::{target}")

            elif message.startswith("GROUP_CALL::"):
                _, group, sender = message.split("::")
                await notify_group(group, sender, f"GROUP_CALL::{group}::{sender}")

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
        print("Server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
