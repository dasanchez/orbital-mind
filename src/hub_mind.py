import asyncio
import websockets
import json
from pprint import pprint

sectors = {}
keywords = {}
wwords = {}

async def hub_mind(uri):
    """ starts the game loop """
    global status
    status = 'idle'
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            # unpack message
            msg = json.loads(msg)
            await message_handler(websocket, msg)

async def message_handler(websocket, msg):
    """
    Parses contents of message.
    """
    global status
    # print(msg)
    if msg['type'] == 'welcome':
        print("Connection established.")
        status = 'connected'
        await state_handler(websocket)
    elif msg['type'] == 'sectors':
        for sector in msg['sectors']:
            sectors[sector['name']] = sector['open']    
        # print(f"Sector names: {sector_names}")
        print(f"Sectors: {sectors}")
    elif msg['type'] == 'response' and msg['msg'] == 'name-accepted':
        status = 'name-accepted'
        print(f"Name '{msg['name']}' accepted.")
        for sector in msg['sectors']:
            sectors[sector['name']] = sector['open']
        print(f"Sectors: {sectors}")     
        await state_handler(websocket)   
    elif msg['type'] == 'response' and msg['msg'] == 'joined-sector':
        status = 'joined-sector'
        print(f"Joined sector {msg['sector']}.")
        await state_handler(websocket)
    elif msg['type'] == 'response' and msg['msg'] == 'team-accepted':
        status = 'joined-team'
        print(f"Joined team {msg['team']}")
        await state_handler(websocket)
    elif msg['type'] == 'response' and msg['msg'] == 'hub-on':
        status = 'hub-role'
        print("Playing as hub.")
    elif  msg['type'] == 'state' and msg['state'] == 'waiting-start':
        if status != 'ready-start':
            status = 'waiting-start'
            if not msg['ready']:
                await state_handler(websocket)
            else:
                status = 'ready-start'
    elif msg['type'] == 'response' and msg['msg'] == 'start-accepted':
        status = 'ready-start'
        print("Ready signal accepted.")
    elif msg['type'] == 'state' and msg['state'] == 'game-start':
        status = 'game-start'
        print("Game has started.")
    elif msg['type'] == 'keys':
        for word in msg['keywords']:
            keywords[word['word']] = word['team']
        # pprint(msg['keywords'])
        # for k,v in msg['keywords'].items():
            # print(k, v)
        print("Keywords:")
        pprint(keywords)
    elif msg['type'] == 'time':
        pass
    else:
        print(msg)

async def state_handler(websocket):
    global status
    if status == 'connected':
        # send name
        print(f"Requesting name.")
        packet = {'type': 'name-request', 'name':'So Much for Subtlety'}
        packet = json.dumps(packet)
        await websocket.send(packet)
    elif status == 'name-accepted':
        # try to join sector
        for name in sectors.keys():
            if sectors[name]:
                print(f"Requesting access to sector {name}.")
                packet = {'type':'join-sector', 'sector': name}
                packet = json.dumps(packet)
                await websocket.send(packet)
                return
    elif status == 'joined-sector':
        print("Trying to join team.")
        # go for orange first
        packet = {'type':'team-request', 'team':'O'}
        packet = json.dumps(packet)
        await websocket.send(packet)
    elif status == 'joined-team':
        print("Requesting hub role.")
        packet = {'type': 'hub-request'}
        packet = json.dumps(packet)
        await websocket.send(packet)
    elif status == 'waiting-start':
        print("Sending Ready signal.")
        packet = {'type': 'ready'}
        packet = json.dumps(packet)
        await websocket.send(packet)

if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(
    asyncio.get_event_loop().run_until_complete(
        hub_mind('ws://localhost:9001'))
    # hub_mind('ws://localhost:9001')
