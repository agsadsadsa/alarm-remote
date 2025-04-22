import asyncio
import websockets

connected = {}

async def handler(websocket):
    user = None
    try:
        async for message in websocket:
            if message.startswith("REGISTER::"):
                parts = message.split("::")
                if len(parts) == 4:
                    _, user, groups, role = parts
                    connected[user] = {"ws": websocket, "groups": groups.split(","), "role": role}
                    await broadcast_users()

            elif message.startswith("GROUP_CALL::"):
                _, sender, group_str, role = message.split("::")
                groups = group_str.split(",")
                for target, info in connected.items():
                    if target != sender and (info["role"] == "admin" or any(g in info["groups"] for g in groups)):
                        await info["ws"].send(f"GROUP_CALL::{sender}::{group_str}::{role}")

            elif message.startswith("KICK::"):
                _, admin, target = message.split("::")
                if admin in connected and connected[admin]["role"] == "admin":
                    if target in connected:
                        await connected[target]["ws"].send("KICKED")
                        await connected[target]["ws"].close()
                        del connected[target]
                        await broadcast_users()

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if user and user in connected:
            del connected[user]
            await broadcast_users()

async def broadcast_users():
    user_list = ",".join(connected.keys())
    for info in connected.values():
        await info["ws"].send(f"USERS::{user_list}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        print("Server started on port 10000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
