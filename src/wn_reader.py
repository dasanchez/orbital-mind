"""
wn_reader.py
wordnet collection
requires nltk to download worndet module
"""
from pprint import pprint
from nltk.corpus import wordnet as wn

def collect_word_data(word, collection, type = 'n'):
    # print(f"{type} synsets for {word}:")
    # print(synset, '\n', dir(synset))
    synsets = wn.synsets(word, type)
    word_dict = dict()
    if synsets:
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
                    hyponyms.append(hypo.name().split('.')[0].split('_'))
                synset_dict['hyponyms'] = hyponyms


            hypers = synset.hypernyms()
            if hypers:
                hypernyms = []
                for hyper in hypers:
                    hypernyms.append(hyper.name().split('.')[0].split('_'))
                synset_dict['hypernyms'] = hypernyms

            synset_list.append(synset_dict)

        word_dict['synsets'] = synset_list
        collection.append(word_dict)
        # print(f"Synset {int(synset.name().split('.')[2])}: {synset.definition()}")
        # antonyms = []

        # hyponyms = synset.hyponyms()
        # hypernyms = synset.hypernyms()
        # lemmas = synset.lemmas()
        # if hyponyms:
        #     hypoSet = set()
        #     print(f"Hyponyms:")
        #     for hyponym in hyponyms:
        #         term = (hyponym.name().split('.')[0].split('_'))
        #         print(term)
        # if hypernyms:
        #     print("Hypernyms:")
        #     for hypernym in hypernyms:
        #         term = (hypernym.name().split('.')[0].split('_'))
        #         print(term)
        # if lemmas:
        #     print("Lemmas:")
        #     for lemma in lemmas:
        #         term = lemma.name().split('.')[-1]
        #         print(term)
        #         if lemma.antonyms():
        #             for ant in lemma.antonyms():
        #                 print(f"Antonym: {ant.name().split('.')[-1]}")

        # attributes = synset.attributes()
        # causes = synset.causes()
        # entailments = synset.entailments()
        # lexname = synset.lexname()
        # region_domains = synset.region_domains()
        # usage_domains = synset.usage_domains()
        
        # if attributes:
        #     print(f"Attributes: {attributes}")
        # if causes:
        #     print(f"Causes: {causes}")
        # if entailments:
        #     print(f"Entailments: {entailments}")

        # if lexname:
        #     print(f"Lex name: {lexname}")
        # if region_domains:
        #     print(f"Region domains: {region_domains}")
        # if usage_domains:
        #     print(f"Usage domains: {usage_domains}")

        # print(f"Examples: {synset.examples()}")
        # print(f"Frame IDs: {synset.frame_ids()}")
        # print(f"Member Holonyms: {synset.member_holonyms()}")
        # print(f"Member Meronyms: {synset.member_meronyms()}")
        # print(f"Part Holonyms: {synset.part_holonyms()}")
        # print(f"Part Meronyms: {synset.part_meronyms()}")
        # print(f"Region domains: {synset.region_domains()}")
        # print(f"Root hypernyms: {synset.root_hypernyms()}")
        # print(f"Similar TOS: {synset.similar_tos()}")
        # print(f"Substance Holonyms: {synset.substance_holonyms()}")
        # print(f"Substance Meronyms: {synset.substance_meronyms()}")
        # print(f"Topic domains: {synset.topic_domains()}")
        # hyp = lambda s:s.hypernyms()
        # print(f"Tree: {synset.tree(hyp)}")
        # print(f"Usage domains: {synset.usage_domains()}")
        # print(f"Verb groups: {synset.verb_groups()}")


# wordfile = open("or_words.txt", 'r')
# words = [line.strip() for line in wordfile]
    # words = line.strip()
words = ['ACNE', 'ACRE', 'ADVERTISE', 'AIRPLANE', 'AISLE', 'BIG']
synsets_collection = list()

for word in words[:20]:
    collect_word_data(word, synsets_collection, 'n')
    collect_word_data(word, synsets_collection, 'v')
    collect_word_data(word, synsets_collection, 'a')
    collect_word_data(word, synsets_collection, 'a')
    # print('')
pprint(synsets_collection)
