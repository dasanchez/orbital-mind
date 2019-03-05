"""
wn_linker.py
generates ranked list of links for each word in the database
"""
import random
from pprint import pprint
from pymongo import MongoClient

word_count = 16

def generate_word_dict(word_set):
    # pick random words
    tempDeck = list(word_set)
    word_dict = dict()
    for _ in range(word_count):
        # print(f"deck has {len(tempDeck)} words")
        pick = random.randint(0, len(tempDeck)-1)
        # print(f"pick: {pick}")
        word_dict[tempDeck[pick]] = 'neutral'
        tempDeck.remove(tempDeck[pick])
    
    # assign keys
    tempDeck = list(word_dict.keys())
    # Flip a coin to decide who goes first
    yes = bool(random.randint(0, 1))
    
    for _ in range(len(word_dict)):
        pick = random.randint(0, len(tempDeck)-1)
        # Stop assigning keys when there are three words left
        if len(tempDeck) > 3:
            if yes:
                word_dict[tempDeck[pick]] = 'yes'
            else:
                word_dict[tempDeck[pick]] = 'no'
            yes = not yes
            tempDeck.remove(tempDeck[pick])

    return word_dict

def clean_links(word, candidate, is_definition = False):
    # build list of acceptable candidates
    fillers = ['a', 'an', 'the', 'or', 'with', 'or', 'to', 'for', 'of',
               'as', 'and', 'very', 'in', 'on', 'who', 'is', 'are',
               'rather']
    raw_list = []
    word = word.lower()
    candidate = candidate.lower()
    # print(f"word: {word}, candidate: {candidate}")
    if ' ' in candidate:
        # split words into list
        raw_list = candidate.split(' ')
        if word in raw_list:
            del raw_list[raw_list.index(word)]
        for term in raw_list:
            if word in term:
                del raw_list[raw_list.index(term)]
            if len(term) <= 2:
                del raw_list[raw_list.index(term)]
    
    elif '-' in candidate:
        # split words into list
        raw_list = candidate.split('-')
        if word in raw_list:
            del raw_list[raw_list.index(word)]
        for term in raw_list:
            if len(term) <= 2:
                del raw_list[raw_list.index(term)]

    elif word in candidate:
        # word is contained in the candidate
        raw_list = [candidate.replace(word,'')]
        for  term in raw_list:
            if len(term) <= 2:
                del raw_list[raw_list.index(term)]
        if 'age' in raw_list:
            del raw_list[raw_list.index('age')]
        if 'ing' in raw_list:
            del raw_list[raw_list.index('ing')]
        if 'ness' in raw_list:
            del raw_list[raw_list.index('ness')]
    elif word == candidate:
        # word is the same as candidate
        pass
    else:
        raw_list = [candidate]

    for term in raw_list:
        if "'" in term:
            temp = term.replace("'", '')
            raw_list.append(temp)
            del raw_list[raw_list.index(term)]
    for term in raw_list:
        if len(term) is 1:
            del raw_list[raw_list.index(term)]

    for filler in fillers:
        while filler in raw_list:
            del raw_list[raw_list.index(filler)]
    return raw_list

def collect_link_data(src_collection, word):
    # returns data from wordnet collection
    wn_entries = src_collection.find({'word':word})
    links = {'word': word}
    link_list = []
    word_list = []
    ranking = 1
    if wn_entries:
        for entry in wn_entries:
            word_type = 'noun'
            if entry['type'] is 'v':
                word_type = 'verb'
            elif entry['type'] is 'a':
                word_type = 'adjective'
            elif entry['type'] is 'r':
                word_type = 'adverb'

            # iterate through synsets
            for synset in entry['synsets']:
                # LEMMAS
                for lemma in synset['lemmas']:
                    lemma_word = lemma['lemma']
                    for term in clean_links(word, lemma_word): 
                        if term and term not in word_list:
                            link_dict = {'link': term,
                                         'synset': synset['id'],
                                         'type': word_type,
                                         'source': 'wordnet',
                                         'ranking': ranking,
                                         'hits': 0,
                                         'attempts': 0,
                                         'score': 0,
                                         'antonym': False}
                            ranking += 1
                            word_list.append(term)
                            link_list.append(link_dict)
                    # ANTONYMS
                    if 'antonyms' in lemma.keys():
                        for ant in lemma['antonyms']:
                            for term in clean_links(word, ant):
                                if term and term not in word_list:
                                    link_dict = {'link': term,
                                                 'synset': synset['id'],
                                                 'type': word_type,
                                                 'source': 'wordnet',
                                                 'ranking': ranking,
                                                 'hits': 0,
                                                 'attempts': 0,
                                                 'score': 0,
                                                 'antonym': True}
                                    ranking += 1
                                    word_list.append(term)
                                    link_list.append(link_dict)
                # HYPONYMS
                if 'hyponyms' in synset.keys():
                    for hypo in synset['hyponyms']:
                        for term in clean_links(word, hypo):
                            if term and term not in word_list:
                                link_dict = {'link': term,
                                             'synset': synset['id'],
                                             'type': word_type,
                                             'source': 'wordnet',
                                             'ranking': ranking,
                                             'hits': 0,
                                             'attempts': 0,
                                             'score': 0,
                                             'antonym': False}
                                ranking += 1
                                word_list.append(term)
                                link_list.append(link_dict)
                # HYPERNYMS
                if 'hypernyms' in synset.keys():
                    for hyper in synset['hypernyms']:
                        for term in clean_links(word, hyper):
                            if term and term not in word_list:
                                link_dict = {'link': term,
                                             'synset': synset['id'],
                                             'type': word_type,
                                             'source': 'wordnet',
                                             'ranking': ranking,
                                             'hits': 0,
                                             'attempts': 0,
                                             'score': 0,
                                             'antonym': False}
                                ranking += 1
                                word_list.append(term)
                                link_list.append(link_dict)
                
                # DEFINITION
                if 'definition' in synset.keys():
                    print(f"Definition for {word}: {synset['definition']}")
                    definition = synset['definition']
                    definition = definition.replace('(', '')
                    definition = definition.replace(')', '')
                    definition = definition.replace(',', '')
                    definition = definition.replace(';', '')
                    for def_word in definition.split():
                        for term in clean_links(word, def_word):
                            if term and term not in word_list:
                                link_dict = {'link': term,
                                             'synset': synset['id'],
                                             'type': word_type,
                                             'source': 'wordnet',
                                             'ranking': ranking,
                                             'hits': 0,
                                             'attempts': 0,
                                             'score': 0,
                                             'antonym': False}
                                ranking += 1
                                word_list.append(term)
                                link_list.append(link_dict)

        links['links'] = link_list
    else:
        print(f"WordNet has no data for {word}")
        return None
    # pprint(links)
    return links

def aggregate_links(src_collection, dest_collection, word):
    # links = {'word': word}
    # is word present in destination collection?
    entries = dest_collection.count_documents({'word':word})
    if entries:
        entry = dest_collection.find_one({'word':word})
        # for word in entry['links']:
            # print(f"Link word: {word['link']}")
        return entry
        # for entry in entries:
            # pprint(entry)
    else:
        # read  data from wordnet
        print("Word not present in hints collection, reading from wordnet one.")
        links = collect_link_data(src_collection, word)
        # dest_collection.insert_one(links)
        return links

# read words in
# word_file = open('src/or_words.txt', 'r')
# word_set = {line.strip().lower() for line in word_file.readlines()}

# word_dict = generate_word_dict(word_set)
# pprint(word_dict)

client = MongoClient()
# open database
db = client['orbital-db']
# source database:
wordnet_collection = db['synsets']
hints_collection = db['hints']

# for k,v in word_dict.items():
    # if v is 'yes':
        # print(f"Links for {k}:")
        # links = aggregate_links(wordnet_collection, links_collection, k)
        # pprint(links)

test_list = ['light', 'school', 'sun', 'dad', 'acre', 'world', 'trip', 'punk', 'mom', 'ice']
# test_list = ['ice']
for test_word in test_list:
    print(f"Links for {test_word}:")
    hints = aggregate_links(wordnet_collection, hints_collection, test_word)
    if hints:
        for link in hints['links']:
            if link['antonym']:
                print(f"{link['link']} (antonym)")
            else:
                print(link['link'])