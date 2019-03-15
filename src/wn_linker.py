"""
wn_linker.py
generates ranked list of links for each word in the database
"""
import random
import difflib
import distance
from pprint import pprint
from nltk.corpus import wordnet as wn
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

def dumb_filter(word1, word2):
    """
    Returns True if word1 and word2 would be accepted.
    Returns False otherwise.
    """
    # Filter 1:
    # Shipwreck / ship
    if word1 in word2 or word2 in word1:
        return False    
    return True

def clean_links(word, candidate, is_definition = False):
    # build list of acceptable candidates
    fillers = ['a', 'an', 'or', 'with', 'or', 'to', 'for', 'of',
               'as', 'and', 'very', 'in', 'on', 'who', 'is', 'are',
               'rather', 'the', 'it', 'at']
    if is_definition:
        fillers.extend(['rather', 'used', 'part', 'inside', 'than', 'from', 'one',
                        'especially', 'no', 'containing', 'which', 'when', 'that',
                        'by', 'per', 'acts', 'some', 'causing', 'make', 'put', 'get',
                        'involving', 'general', 'distinctive', 'all', 'your', 'how',
                        'appear', 'you', 'we', 'can', 'be', 'considered', 'separately',
                        'terms', 'out', 'set', 'off', 'if', 'may', 'like', 'any', 'more',
                        'including', 'resembling', 'true', 'toward', 'similar', 'most', 
                        'form', 'etc.', 'such', 'ones', 'exhibited', 'exhibiting', 'characterized',
                        'markedly', 'forth', 'two', 'something', 'consisting', 'holding',
                        'produced', 'removed', 'so', 'about', 'has', 'been', 'loosely',
                        'without', 'displaying', 'possessing', 'brightly', 'able', 'others',
                        'high', 'low', 'other', 'around', 'do', 'needed', 'during', 'usually',
                        'but', 'term', 'probably', 'derived', 'not', 'this', 'concern', 'being',
                        'designed', 'example', 'answering', 'performing', 'closely', 'strictly',
                        'either', 'while', 'bring', 'put', 'above', 'below', 'its', 'etc',
                        'formerly', 'their'])

    raw_list = []
    word = word.lower()
    candidate = candidate.lower()

    if ' ' in candidate:
        raw_list.extend([term for term in candidate.split(' ') if term not in raw_list])
        for term in raw_list:
            if '-' in term:
                raw_list.extend(term.split('-'))
                del raw_list[raw_list.index(term)]
    elif '-' in candidate:
        raw_list.extend(candidate.split('-'))
    elif ':' in candidate:
        raw_list.extend(candidate.split(':'))
    else:
        raw_list= [candidate]
    
    for term in raw_list:
        if word in term:
            raw_list.append(term.replace(word,''))
            del raw_list[raw_list.index(term)]
    for term in raw_list:
        if len(word) > 3 and word[:-1] in term:
            print(f"Removing {term}")
            del raw_list[raw_list.index(term)]
    for term in raw_list:
        if "'" in term:
            temp = term.replace("'", '')
            raw_list.append(temp)
            del raw_list[raw_list.index(term)]
    for term in raw_list:
        if '"' in term:
            temp = term.replace('"', '')
            raw_list.append(temp)
            del raw_list[raw_list.index(term)]
    for term in raw_list:
        if '`' in term:
            temp = term.replace('`', '')
            raw_list.append(temp)
            del raw_list[raw_list.index(term)]
    # for term in raw_list:
    #     if (1-distance.sorensen(word, term)) > threshold:
    #     # if difflib.SequenceMatcher(None, word, term).ratio() > threshold:
    #         print(f"Skipping '{term}'.")
    #         del raw_list[raw_list.index(term)]
    for term in raw_list:
        if len(term) <= 2:
            del raw_list[raw_list.index(term)]
    
    if 'age' in raw_list:
        del raw_list[raw_list.index('age')]
    if 'ing' in raw_list:
        del raw_list[raw_list.index('ing')]
    if 'ness' in raw_list:
        del raw_list[raw_list.index('ness')]

    for filler in fillers:
        while filler in raw_list:
            del raw_list[raw_list.index(filler)]
    
    filtered_words = []

    while '' in raw_list:
        del raw_list[raw_list.index('')]

    for term in raw_list:
        if not dumb_filter(word, term):
            print(f"Dumb filter removed '{term}'.")
            filtered_words.append(term)
            del raw_list[raw_list.index(term)]
    
    for term in raw_list:
        for character in term:
            if character.isdigit():
                del raw_list[raw_list.index(term)]
                break
    
    return raw_list, filtered_words

def build_link_entry(word, synset_id, word_type, ranking, antonym = False):
    link_entry = {'link': word,
                  'synset': synset_id,
                  'type': word_type,
                  'source': 'wordnet',
                  'ranking': ranking,
                  'hits': 0,
                  'attempts': 0,
                  'score': 0.5,
                  'antonym': antonym}
    return link_entry

def build_link_list(collection_entry, word):
    link_list = []
    word_list = []
    word_type = 'noun'
    ranking = 1
    
    if collection_entry['type'] is 'v':
        word_type = 'verb'
    elif collection_entry['type'] is 'a':
        word_type = 'adjective'
    elif collection_entry['type'] is 'r':
        word_type = 'adverb'

    filtered_list = []
    # iterate through synsets
    for synset in collection_entry['synsets']:
        # LEMMAS
        for lemma in synset['lemmas']:
            lemma_word = lemma['lemma']
            accepted, purged = clean_links(word, lemma_word)
            filtered_list.extend(purged)
            for term in accepted: 
                if term and term not in word_list:
                    link_dict = build_link_entry(term, synset['id'], word_type, ranking)
                    ranking += 1
                    word_list.append(term)
                    link_list.append(link_dict)
            # ANTONYMS
            if 'antonyms' in lemma.keys():
                for ant in lemma['antonyms']:
                    accepted, purged = clean_links(word, ant)
                    filtered_list.extend(purged)
                    for term in accepted:
                        if term and term not in word_list:
                            link_dict = build_link_entry(term, synset['id'], word_type, ranking, antonym=True)
                            ranking += 1
                            word_list.append(term)
                            link_list.append(link_dict)
        # HYPONYMS
        if 'hyponyms' in synset.keys():
            for hypo in synset['hyponyms']:
                accepted, purged = clean_links(word, hypo)
                filtered_list.extend(purged)
                for term in accepted:
                    if term and term not in word_list:
                        link_dict = build_link_entry(term, synset['id'], word_type, ranking)
                        ranking += 1
                        word_list.append(term)
                        link_list.append(link_dict)
        # HYPERNYMS
        if 'hypernyms' in synset.keys():
            for hyper in synset['hypernyms']:
                accepted, purged = clean_links(word, hyper)
                filtered_list.extend(purged)
                for term in accepted:
                    if term and term not in word_list:
                        link_dict = build_link_entry(term, synset['id'], word_type, ranking)
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
            definition = definition.replace(':', '')
            # remove digits:
            definition = ''.join([i for i in definition if not i.isdigit()])
            for def_word in definition.split():
                accepted, purged = clean_links(word, def_word, is_definition=True)
                filtered_list.extend(purged)
                for term in accepted:
                    if term and term not in word_list:
                        link_dict = build_link_entry(term, synset['id'], word_type, ranking)
                        ranking += 1
                        word_list.append(term)
                        link_list.append(link_dict)

    return link_list, filtered_list

def collect_wordnet_data(word, type='n'):
    """
    Reads synsets from WordNet module.
    If synsets found, returns a dictionary with all available data.
    Otherwise, returns False.
    """
    synsets = wn.synsets(word, type)

    if synsets:
        word_dict = dict()
        word_dict['word'] = word
        word_dict['type'] = type
        synset_list = []
        for synset in wn.synsets(word, type):
            synset_dict = dict()

            synset_dict['id'] = int(synset.name().split('.')[2])

            synset_dict['definition'] = synset.definition()

            lemmas = []
            for lemma in synset.lemmas():
                lemma_dict = {'lemma': lemma.name().replace('_', ' ')}
                ants = lemma.antonyms()
                if ants:
                    antonyms = []
                    for ant in ants:
                        antonyms.append(ant.name().split('.')[-1].replace('_', ' '))
                    lemma_dict['antonyms'] = antonyms
                lemmas.append(lemma_dict)
            synset_dict['lemmas'] = lemmas

            hypos = synset.hyponyms()
            if hypos:
                hyponyms = []
                for hypo in hypos:
                    hyponyms.append(hypo.name().split('.')[0].replace('_', ' '))
                synset_dict['hyponyms'] = hyponyms

            hypers = synset.hypernyms()
            if hypers:
                hypernyms = []
                for hyper in hypers:
                    hypernyms.append(hyper.name().split('.')[0].replace('_', ' '))
                synset_dict['hypernyms'] = hypernyms

            synset_list.append(synset_dict)

        word_dict['synsets'] = synset_list
        return word_dict
    return False

def collect_link_data(src_collection, word):
    # returns data from wordnet collection
    links = {'word': word, 'links':[]}
    purged_words = []
    if src_collection.count_documents({'word':word}):
        for entry in src_collection.find({'word':word}):
            link_list, filtered_list = build_link_list(entry, word)
            links['links'].extend(link_list)
            purged_words.extend(filtered_list)
            # pprint(links)
            # links['links'].extend(build_link_list(entry, word))
    else:
        print(f"Databases have no data for '{word}',",
               "attempting to register from WordNet corpus...")
        new_entries = 0
        eval_types = ['n', 'v', 'a', 'r']
        for eval_type in eval_types:
            synset = collect_wordnet_data(word, eval_type)
            if synset:
                print(f"Inserting new entry: {word}, {eval_type}")
                src_collection.insert_one(synset)
                new_entries += 1
        if new_entries:
            for entry in src_collection.find({'word':word}):
                # links['links'].extend(build_link_list(entry, word))
                link_list, filtered_list = build_link_list(entry, word)
                links['links'].extend(link_list)
                purged_words.extend(filtered_list)
        else:
            print("Found no WordNet data for '{word}'")
            return None
    purged_words = set(purged_words)
    print(f"Filtered words: {purged_words}")
    # pprint(links)
    if purged_words:
        for link in links['links']:
            for p_word in purged_words:
                if p_word == link['link'] or p_word in link['link'] or link['link'] in p_word:
                    print(f"Removing {link['link']}")
                    del links['links'][links['links'].index(link)]


    return links

def aggregate_links(src_collection, dest_collection, word):
    # links = {'word': word}
    # is word present in destination collection?
    if dest_collection.count_documents({'word':word}):
        entry = dest_collection.find_one({'word':word})
        return entry
    else:
        # read  data from wordnet
        print("Word not present in hints collection, reading from synsets one...")
        links = collect_link_data(src_collection, word)
        dest_collection.insert_one(links)
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
links_collection = db['links']

# for k,v in word_dict.items():
    # if v is 'yes':
        # print(f"Links for {k}:")
        # links = aggregate_links(wordnet_collection, links_collection, k)
        # pprint(links)

# test_list = ['light', 'school', 'sun', 'dad', 'acre', 'world',
#              'trip', 'punk', 'mom', 'ice', 'rib', 'pomp', 'music',
#              'macho', 'jump', 'fringe', 'dust', 'brave', 'clown',
#              'eureka', 'game', 'goodbye', 'hedge', 'letter', 'job',
#              'twins', 'space', 'ice']

test_list = ['archeologist']
# threshold = 0.8
for test_word in test_list:
    hints = aggregate_links(wordnet_collection, links_collection, test_word)
    if hints:
        print(f"{len(hints['links'])} links for {test_word}:")
        for link in hints['links']:
            if link['antonym']:
                print(f"{link['link']} (antonym)")
            else:
                print(link['link'])