"""
wn_reader.py
wordnet collection
requires nltk to download worndet module
"""
from pprint import pprint
from nltk.corpus import wordnet as wn
from pymongo import MongoClient


def collect_word_data(word, type='n'):
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

# open database
client = MongoClient()
db = client['orbital-db']
synset_collection = db['synsets']

# collect WordNet data
wordfile = open("src/or_words.txt", 'r')
words = [line.strip().lower() for line in wordfile]

eval_types = ['n', 'v', 'a', 'r']
new_words = 0
new_entries = 0
for word in words:
    # print(f"Looking up {word}...")
    if not synset_collection.count_documents({'word':word}):
        print(f"Word '{word}' not found in database.")
        new_words += 1
        for eval_type in eval_types:
            synset = collect_word_data(word, eval_type)
            if synset:
                print(f"Inserting new entry: {word}, {eval_type}")
                synset_collection.insert_one(synset)
                new_entries += 1
if new_words:
    print(f"Found {new_words} new words, registered {new_entries}.")
else:
    print("Done.")
