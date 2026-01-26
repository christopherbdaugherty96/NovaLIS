import asyncio
import json
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/ws"
    async with websockets.connect(uri) as ws:
        print("CONNECTED")
        await ws.send(json.dumps({"text": "weather"}))
        print("SENT weather")
        response = await ws.recv()
        print("RESPONSE:", response)

asyncio.run(test())
