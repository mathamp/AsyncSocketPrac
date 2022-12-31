import asyncio
from websockets import connect


async def hello(uri):
    async with connect(uri) as websocket:
        await websocket.send("Hello world!")
        ret = await websocket.recv()
        print(ret)


asyncio.run(hello("ws://localhost:8765"))
