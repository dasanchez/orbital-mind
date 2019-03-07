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
- [ ] Reject words that are too similar:
  - mom: ma, mum, mummy, mommy > mother
  - macho: machismo > masculine
  - dad: daddy, dada > father, papa
- Samples words: school, sun, freight
- [ ] Hints are presented to the user in order to get a ranking or to be removed.
- [ ] User provides additional links if possible and assigns a ranking.
