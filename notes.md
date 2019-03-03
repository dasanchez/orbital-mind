# Orbital Mind

## Roadmap

The goal is to produce a bot able to generate a hint based on a list of words, some of which we want guessed and some of which we want to avoid.

## Milestones

- [ ] Program reads all words from the Orbitals word set and  builds a database with all WordNet-provided data (lemmas + antonyms, hyponyms, hypernyms, definition)
- [ ] Program receives 20 random words - use piece of Orbitals to generate the word set.
- [ ] Program goes through each word and generates a potential list of hints if the word hasn't been seen before.
- [ ] Hints are presented to the user in order to get a ranking.
- [ ] User provides additional links if possible and assigns a ranking.