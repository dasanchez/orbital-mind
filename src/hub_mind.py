import random
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
        self.hint = ''
        self.target = ''
        self.websocket = websocket
        self.mongo_client = MongoClient()
        self.db = self.mongo_client['orbital-db']
        self.synsets_collection = self.db['synsets']
        self.links_collection = self.db['links']
        self.hub_names = ['So Much for  Subtlety',
                          'Dressed Up To Party',
                          'Fixed Grin',
                          'Now We Try It My Way',
                          'Conventional Wisdom',
                          'Determinist',
                          'Flexible  Demeanour',
                          'Use Psychology']

    def update_rankings(self, links):
        # links = sorted(links, key=lambda k: k['score'], reverse=True)
        # pprint(ranked_links)
        return sorted(links, key=lambda k: k['score'], reverse=True)

    def hint_rejected(self):
        word_entry = self.links_collection.find_one({'word':self.target.lower()})
        if word_entry:
            link_entries = word_entry['links']
            for entry in link_entries:
                if entry.get('link') == self.hint:
                    print(f"Word {self.hint} rejected, updating database entry.")
                    entry['attempts'] = entry['attempts'] + 10
                    if entry['hits'] / entry['attempts'] == 0: # give all words a chance
                        entry['score'] = 0.1
                    else:
                        entry['score'] = entry['hits'] / entry['attempts']
                    break
            word_entry['links'] = self.update_rankings(link_entries)
            self.links_collection.update({'word':self.target.lower()}, word_entry)

    def hint_failure(self):
        print("Hint failed")
        word_entry = self.links_collection.find_one({'word':self.target.lower()})
        if word_entry:
            link_entries = word_entry['links']
            for entry in link_entries:
                if entry.get('link') == self.hint:
                    print(f"Word {self.hint} missed, updating database entry.")
                    entry['attempts'] = entry['attempts'] + 1
                    if entry['hits'] / entry['attempts'] == 0: # give all words a chance
                        entry['score'] = 0.1
                    else:
                        entry['score'] = entry['hits'] / entry['attempts']
                    break
            word_entry['links'] = self.update_rankings(link_entries)
            self.links_collection.update({'word':self.target.lower()}, word_entry)

    def hint_success(self):
        word_entry = self.links_collection.find_one({'word':self.target.lower()})
        if word_entry:
            link_entries = word_entry['links']
            for entry in link_entries:
                if entry.get('link') == self.hint:
                    print(f"Word {self.hint} accepted, updating database entry.")
                    entry['attempts'] = entry['attempts'] + 1
                    entry['hits'] = entry['hits'] + 1
                    entry['score'] = entry['hits'] / entry['attempts']
                    break
            word_entry['links'] = self.update_rankings(link_entries)
            self.links_collection.update({'word':self.target.lower()}, word_entry)

    async def respond_to_hint(self, word):
        """ Approve all hints for now. """
        packet = {'type': 'hint-response', 'response': True}
        packet = json.dumps(packet)
        await self.websocket.send(packet)

    async def submit_hint(self):
        """ Send a hint to match a single keyword. """
        # Find a word that has not been guessed yet.
        self.target = self.remaining_words[0]
        print(f"Looking for a hint for {self.target}")
        
        # Gather list of links first
        links = wn_linker.aggregate_links(self.synsets_collection, self.links_collection, self.target.lower())
        if links['links']:
            print("Found the following links:")
            if len(links['links']) >= 5:
                pprint(links['links'][:5])
            else:
                pprint(links['links'])
            self.hint = links['links'][0]['link']
        else:
            print("No links found.")
            self.hint = "testword"    
        packet = {'type': 'hint', 'hint': self.hint, 'guesses': 1}
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
            print(msg)
            # did someone from our team guess?
            if msg['guesserTeam'] == self.team:
                # is it the word we wanted?
                if msg['word'] == self.target:
                    # update the ranking for our hint!
                    self.hint_success()
                else:
                    # no, some other word got guessed
                    self.hint_failure()
            if msg['word'] in self.remaining_words:
                self.remaining_words.remove(msg['word'])
        elif msg['type'] == 'msg' and 'REJECTED' in msg['msg']:
            # was our hint rejected?
            if self.team != msg['team']:
                self.hint_rejected()
        elif msg['type'] == 'time':
            pass
        else:
            print(msg)
        
    async def state_handler(self):
        if self.status == 'connected':
            # send name
            print(f"Requesting name.")
            random_name = random.randint(0, 7)
            packet = {'type': 'name-request', 'name':self.hub_names[random_name]}
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

