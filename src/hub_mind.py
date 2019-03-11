import asyncio
import websockets
import json
from pprint import pprint
from pymongo import MongoClient
import wn_linker

class HubMind:
    """ Orbital-playing bot that plays as hub."""
    
    def __init__(self, websocket):
        self.status = 'idle'
        self.sectors = dict()
        self.keywords = dict()
        self.words = dict()
        self.remaining_words = list()
        self.team = ''
        self.websocket = websocket
        self.mongo_client = MongoClient()
        self.db = self.mongo_client['orbital-db']
        self.synsets_collection = self.db['synsets']
        self.links_collection = self.db['links']

    async def respond_to_hint(self, word):
        """ Approve all hints for now. """
        packet = {'type': 'hint-response', 'response': True}
        packet = json.dumps(packet)
        await self.websocket.send(packet)

    async def submit_hint(self):
        """ Send a hint to match a single keyword. """
        # Find a word that has not been guessed yet.
        word_to_match = self.remaining_words[0]
        print(f"Looking for a hint for {word_to_match}")

        # Gather list of links first
        links = wn_linker.aggregate_links(self.synsets_collection, self.links_collection, word_to_match)
        if links['links']:
            print("Found the following links:")
            pprint(links)
            hint = links['links'][0]['link']
        else:
            print("No links found.")
            hint = "testword"    
        packet = {'type': 'hint', 'hint': hint, 'guesses': 1}
        packet = json.dumps(packet)
        await self.websocket.send(packet)

    async def message_handler(self, msg):
        """ Parses incoming packets. """
        if msg['type'] == 'welcome':
            print("Connection established.")
            self.status = 'connected'
            await self.state_handler()
        elif msg['type'] == 'sectors':
            for sector in msg['sectors']:
                self.sectors[sector['name']] = sector['open']    
            print("Sectors:")
            pprint(self.sectors)
        elif msg['type'] == 'response' and msg['msg'] == 'name-accepted':
            self.status = 'name-accepted'
            print(f"Name '{msg['name']}' accepted.")
            for sector in msg['sectors']:
                self.sectors[sector['name']] = sector['open']
            print("Sectors:")
            pprint(self.sectors)     
            await self.state_handler()   
        elif msg['type'] == 'response' and msg['msg'] == 'joined-sector':
            self.status = 'joined-sector'
            print(f"Joined sector {msg['sector']}.")
            await self.state_handler()
        elif msg['type'] == 'response' and msg['msg'] == 'team-accepted':
            self.status = 'joined-team'
            self.team = msg['team']
            print(f"Joined team {msg['team']}")
            await self.state_handler()
        elif msg['type'] == 'response' and msg['msg'] == 'hub-on':
            self.status = 'hub-role'
            print("Playing as hub.")
        elif msg['type'] == 'state' and msg['state'] == 'waiting-start':
            if self.status != 'ready-start':
                self.status = 'waiting-start'
                if not msg['ready']:
                    await self.state_handler()
                else:
                    self.status = 'ready-start'
        elif msg['type'] == 'response' and msg['msg'] == 'start-accepted':
            self.status = 'ready-start'
            print("Ready signal accepted.")
        elif msg['type'] == 'state' and msg['state'] == 'game-start':
            self.status = 'game-start'
            # Clear words and keywords
            self.keywords.clear()
            self.words.clear
            self.remaining_words.clear()
            print("Game has started.")
        elif msg['type'] == 'keys':
            for word in msg['keywords']:
                self.keywords[word['word']] = word['team']
            for k,v in self.keywords.items():
                if v == self.team:
                    self.remaining_words.append(k)
            print("Keywords:")
            pprint(self.keywords)
        elif  msg['type'] == 'words':
            for word in msg['words']:
                self.words[word['word']] = word['team']
            print("Public words:")
            pprint(self.words)
        elif msg['type'] == 'state' and msg['state'] == 'hint-submission':
            if msg['turn'] == self.team:
                self.status = 'submit-hint'
                print("Submitting hint.")
                await self.submit_hint()
            else:
                self.status = 'waiting-hint'
        elif msg['type'] == 'state' and msg['state'] == 'hint-response':
            if msg['turn'] != self.team:
                self.status = 'respond-hint'
                print("Responding to hint.")
                await self.respond_to_hint(msg['hint'])
            else:
                self.status = 'waiting-response'
        elif msg['type'] == 'state' and msg['state'] == 'game-over':
            if self.status != 'replay-ready':
                print(f"Game over: {msg['prompt']}")
                self.status = 'game-over'
                await self.state_handler()
        elif msg['type'] == 'replay-ack':
            self.status = 'replay-ready'
            print("Replay signal acknowledged.")
        elif msg['type'] == 'guess':
            if msg['word'] in self.remaining_words:
                self.remaining_words.remove(msg['word'])
        elif msg['type'] == 'time':
            pass
        else:
            print(msg)
        
    async def state_handler(self):
        if self.status == 'connected':
            # send name
            print(f"Requesting name.")
            packet = {'type': 'name-request', 'name':'So Much for Subtlety'}
            packet = json.dumps(packet)
            await self.websocket.send(packet)
        elif self.status == 'name-accepted':
            # try to join sector
            for name in self.sectors.keys():
                if self.sectors[name]:
                    print(f"Requesting access to sector {name}.")
                    packet = {'type':'join-sector', 'sector': name}
                    packet = json.dumps(packet)
                    await self.websocket.send(packet)
                    return
        elif self.status == 'joined-sector':
            print("Trying to join team.")
            # go for orange first
            packet = {'type':'team-request', 'team':'O'}
            packet = json.dumps(packet)
            await self.websocket.send(packet)
        elif self.status == 'joined-team':
            print("Requesting hub role.")
            packet = {'type': 'hub-request'}
            packet = json.dumps(packet)
            await self.websocket.send(packet)
        elif self.status == 'waiting-start':
            print("Sending Ready signal.")
            packet = {'type': 'ready'}
            packet = json.dumps(packet)
            await self.websocket.send(packet)
        elif self.status == 'game-over':
            print("Sending Replay signal.")
            packet = {'type': 'replay'}
            packet = json.dumps(packet)
            await self.websocket.send(packet)

