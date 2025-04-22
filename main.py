import asyncio
import websockets

connected_users = {}

async def notify_user_list():
    if connected_users:
        msg = "USERS::" + ",".join(connected_users.keys())
        await asyncio.gather(*[ws.send(msg) for ws in connected_users.values()])

async def handler(websocket):
    try:
        raw_nick = await websocket.recv()
        if not raw_nick.startswith("NICK::"):
            await websocket.close()
            return

        nickname = raw_nick[6:]
        connected_users[nickname] = websocket
        print(f"{nickname} connected")
        await notify_user_list()

        async for message in websocket:
            print(f"{nickname}: {message}")
            if message.startswith("CALL::"):
                for ws in connected_users.values():
                    await ws.send(message)
            elif message.startswith("PRIVATE_CALL::"):
                _, from_user, to_user = message.split("::")
                if to_user in connected_users:
                    await connected_users[to_user].send(message)

    except:
        pass
    finally:
        for name, ws in list(connected_users.items()):
            if ws == websocket:
                print(f"{name} disconnected")
                del connected_users[name]
        await notify_user_list()

async def main():
    port = int(os.environ.get("PORT", 10000))
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    import os
    asyncio.run(main())
