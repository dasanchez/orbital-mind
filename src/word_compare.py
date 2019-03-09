'''
word_compare.py
Establishes how similar two words are and rejects the link if they are two similar.
'''
import difflib, distance
import math
from pprint import pprint

def tri_window(word):
    # Generate a list of strings that break up the word into segments of three characters
    return [word[index:index+3] for index in range(0, len(word)-2)]

def is_too_close(word, candidate):
    """
    Compares word to match against candidate.
    Returns True if it's too close.
    Returns False if it's OK.
    """
    vowels = ['a','e','i','o','u']
    # 1st pass: word is present in candidate
    if word in candidate:
        print("Match on 1st pass: ", end='')
        return True
    
    # 2nd pass: three-letter window check
    # word is present in a three-letter window with one letter forcibly matched
    if len(word)==3:
        for window in tri_window(candidate):
            # replace the second letter of the word with the middle letter of the window 
            temp = word[0] + window[1] + word[2]
            if temp == window and word[1] in vowels:
                print("Match on 2nd pass: ", end='')
                return True
            # replace the third letter of the word with the last letter of the candidate
            if len(candidate) < 5:
                temp = word[:2] + window[2]
                if temp == window and word[2] in vowels:
                    print("Match on 2nd pass: ", end='')
                    return True

    # 3rd pass: remove last letter of the word to match
    if word[:-1] in candidate and len(word) > 3:
        print(f"Match on 3rd pass: ", end='')
        return True
    
    # 4th pass: remove last letter of the word to match
    if word[:-2] in candidate and len(word) > 4:
        print(f"Match on 4rd pass: ", end='')
        return True

    # 5th pass: remove all vowels of the word to match
    cons = ''.join([l for l in word if l not in vowels])
    if cons == candidate:
        print("Match on 5th pass: ", end='')
        return True
    
    return False

words = ['dad', 'sun', 'mom', 'macho', 'game', 'mast', 'space', 'ice', 'age', 'romp']
dad_list = ['dada', 'daddy', 'pa', 'papa', 'pop', 'pappa', 'father']
sun_list = ['sunny', 'sunlight', 'light', 'star', 'sunday', 'insolate']
mom_list = ['mum', 'mommy', 'mummy', 'ma', 'mother', 'mama', 'mamma']
macho_list = ['machismo', 'masculine', 'mch']
game_list = ['gamy', 'gamey', 'wild', 'winner']
mast_list = ['foremast', 'jiggermast', 'pole', 'mainmast', 'mizzenmast', 'masts', 'topmast']
space_list = ['spacing', 'spatial', 'expanse', 'separate', 'distance', 'spc']
ice_list = ['icy', 'icarus', 'cold']
age_list = ['ape', 'ago', 'are', 'pre', 'ace']
romp_list = ['rope', 'rombhus', 'rosy', 'rode']

lists = [dad_list, sun_list, mom_list, macho_list,
         game_list, mast_list, space_list, ice_list, age_list, romp_list]

for i in range(0, len(words)):
    removals = []
    for word in lists[i]:
        if is_too_close(words[i], word):
            print(words[i], word)
            removals.append(word)
    for removal in removals:
        del lists[i][lists[i].index(removal)]

pprint(words)
pprint(lists)
