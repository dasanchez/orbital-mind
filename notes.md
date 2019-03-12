# Orbital Mind

## Roadmap

The goal is to produce a bot able to generate a hint based on a list of words, some of which we want guessed and some of which we want to avoid.

## Milestones

- [X] Program reads all words from the Orbitals word set and builds a database with all WordNet-provided data (lemmas + antonyms, hyponyms, hypernyms, definition)
  - See `wn_reader.py`
- [X] Program receives 16 random words - use piece of Orbitals to generate the word set. Some of them we want to match, but some of them we don't.
  - See `wn_linker.py`
- [X] Program goes through each word and generates a potential list of hints if the word hasn't been seen before.
- [X] For a compound entry (e.g. "inflammatory_disease"), file each term separately.
- [X] When qualifying matches that include the word itself, keep the non-offending part if the word exists (e.g., sun: sunshine -> keep "shine").
- [X] Save each word from the definition separately as well.
- **Schema**
{
    word: 'sun',
    links [
        {
            link: 'bathe',
            source: 'learned',
            rank: 5,
            hits: 0,
            type: 'verb'
            synset: 2
        },
        {
            link: 'light',
            source: 'wordnet',
            rank: 1,
            hits: 0
            type: 'noun'
            synset: 1
        }
    ]
}
- [x] Reject words that are too similar:
  - mom: ma, mum, mummy, mommy > mother
  - macho: machismo > masculine
  - dad: daddy, dada > father, papa
  - game: gamy
- [ ] Assess and address
  - [X] "password" results in "watchword".

    I would reject this, because "word" is present in both.
  
  - [X] "wax" results in "bayberry"
  
    I would accept this.
  
  - [X] "sash" results in "window"
  
    I would accept this.
  
  - [X] "squint" results in "strabismus"
  
    I would accept this.

  - [X] "shipwreck" results in "ship"

    I would reject this, because "ship" matches the **beginning** of the word to match.

  - [X] "lifestyle" results in "life"

    I would reject this, because "life" matches the **beginning** of the word to match.

  - [X] "archaeologist" results in "archeologist"

    I would reject this, because there is a one-letter difference between two long (>10 letters) words.

  - [X] "loyalty" results in "dis" (as in, disloyalty)

    I would accept this.

  - [X] "gray" results in "grey"

    I would reject this, because only one vowel in two four-letter words is different.

  - [ ] "chew" results in "chaw"

    I would reject this, because only one vowel in two four-letter words is different.

  - [ ] "bobsled" results in "short" - but there is a SHORT in the word board already
- [ ] Hints are presented to the user in order to get a ranking or to be removed.
- [ ] User provides additional links if possible and assigns a ranking.
