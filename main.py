import asyncio
import websockets
import os

connected_users = {}  # 昵称 -> websocket
user_groups = {}      # 昵称 -> 分组名
group_members = {}    # 分组名 -> [昵称]

async def notify_user_list():
    if connected_users:
        msg = "USERS::" + ",".join(connected_users.keys())
        await asyncio.gather(*[ws.send(msg) for ws in connected_users.values()])

async def notify_group_list():
    for nickname, ws in connected_users.items():
        groups = [group for group, members in group_members.items() if nickname in members]
        msg = "GROUPS::" + ",".join(groups)
        await ws.send(msg)

async def handler(websocket):
    try:
        raw_nick = await websocket.recv()
        if not raw_nick.startswith("NICK::"):
            await websocket.close()
            return

        nickname = raw_nick[6:]
        connected_users[nickname] = websocket

        # 分配分组（示例：固定分组）
        if nickname in ["小红", "小明", "小刚"]:
            group = "teamA"
        elif nickname in ["小李", "小王", "小赵"]:
            group = "teamB"
        else:
            group = "teamC"

        user_groups[nickname] = group
        group_members.setdefault(group, []).append(nickname)

        print(f"{nickname} connected")
        await notify_user_list()
        await notify_group_list()

        async for message in websocket:
            print(f"{nickname}: {message}")
            if message.startswith("CALL::"):
                for ws in connected_users.values():
                    await ws.send(message)
            elif message.startswith("PRIVATE_CALL::"):
                _, from_user, to_user = message.split("::")
                if to_user in connected_users:
                    await connected_users[to_user].send(message)
            elif message.startswith("GROUP_CALL::"):
                _, group, from_user = message.split("::")
                members = group_members.get(group, [])
                for user in members:
                    if user != from_user and user in connected_users:
                        await connected_users[user].send(message)
            elif message.startswith("GET_GROUPS::"):
                _, nick = message.split("::")
                groups = [group for group, members in group_members.items() if nick in members]
                msg = "GROUPS::" + ",".join(groups)
                await websocket.send(msg)

    except:
        pass
    finally:
        for name, ws in list(connected_users.items()):
            if ws == websocket:
                print(f"{name} disconnected")
                del connected_users[name]
                group = user_groups.get(name)
                if group and name in group_members.get(group, []):
                    group_members[group].remove(name)
                if name in user_groups:
                    del user_groups[name]
        await notify_user_list()
        await notify_group_list()

async def main():
    port = int(os.environ.get("PORT", 10000))
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
