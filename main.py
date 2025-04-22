clients = set()
user_nicknames = {}

async def register(ws):
    clients.add(ws)

async def unregister(ws):
    clients.discard(ws)
    user_nicknames.pop(ws, None)
    await broadcast_users()

async def broadcast_users():
    names = ",".join(user_nicknames.values())
    message = f"USERS::{names}"
    await asyncio.gather(*[client.send(message) for client in clients if not client.closed])

async def handler(ws):
    await register(ws)
    try:
        async for msg in ws:
            if msg.startswith("NICK::"):
                nickname = msg[6:]
                user_nicknames[ws] = nickname
                await broadcast_users()
            elif msg.startswith("CALL::"):
                sender = msg[6:]
                await asyncio.gather(*[c.send(f"CALL::{sender}") for c in clients if c != ws])
            elif msg.startswith("PRIVATE_CALL::"):
                _, sender, receiver = msg.split("::")
                for client, name in user_nicknames.items():
                    if name == receiver:
                        await client.send(f"PRIVATE_CALL::{sender}::{receiver}")
                        break
    finally:
        await unregister(ws)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 10000):
        await asyncio.Future()
