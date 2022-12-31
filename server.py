import asyncio
from websockets import serve


async def echo(websocket):
    print("Got Message")
    async for message in websocket:
        print(message)
        #await websocket.send(message)


async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
