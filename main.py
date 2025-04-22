import asyncio
import websockets

clients = set()

async def handler(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            # 广播给所有其他客户端
            for client in clients:
                if client != websocket:
                    await client.send(message)
    finally:
        clients.remove(websocket)

async def main():
    port = 10000  # Render 上我们固定使用这个端口
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"WebSocket server running on port {port}")
        await asyncio.Future()  # 永不退出

asyncio.run(main())
