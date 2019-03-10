import asyncio
import websockets
import json
from pprint import pprint
from hub_mind import HubMind

async def loop_start(uri):
    """ starts the game loop """
    async with websockets.connect(uri) as websocket:
        mind = HubMind(websocket)
        while True:
            msg = await websocket.recv()
            msg = json.loads(msg)
            await mind.message_handler(msg)

if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(
    asyncio.get_event_loop().run_until_complete(
        loop_start('ws://localhost:9001'))
    # hub_mind('ws://localhost:9001')
