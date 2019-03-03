"""
wn_linker.py
generates ranked list of links for each word in the database
"""
from pprint import pprint
from pymongo import MongoClient

def build_word_links(word, type = 'n'):
    pass
    '''
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
                lemma_dict = {'lemma': lemma.name()}
                ants = lemma.antonyms()
                if ants:
                    antonyms = []
                    for ant in ants:
                        antonyms.append(ant.name().split('.')[-1])
                    lemma_dict['antonyms'] = antonyms
                lemmas.append(lemma_dict)
            synset_dict['lemmas'] = lemmas

            hypos = synset.hyponyms()
            if hypos:
                hyponyms = []
                for hypo in hypos:
                    hyponyms.append(hypo.name().split('.')[0])
                synset_dict['hyponyms'] = hyponyms


            hypers = synset.hypernyms()
            if hypers:
                hypernyms = []
                for hyper in hypers:
                    hypernyms.append(hyper.name().split('.')[0])
                synset_dict['hypernyms'] = hypernyms

            synset_list.append(synset_dict)

        word_dict['synsets'] = synset_list
        return word_dict
    return False
    '''
        

# open database
client = MongoClient()
db = client['orbital-db']
# source database:
synset_collection = db['synsets']
# destination database:

# for word in words:
    # print(f"Looking up {word}...")
    # for eval_type in eval_types:
        # synset = collect_word_data(word, eval_type)
        # if synset:
            # synset_collection.insert_one(synset)
# print("Done.")

