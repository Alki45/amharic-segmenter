# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - Unreleased

### Added
- NLTK-style API: `sent_tokenize`, `word_tokenize`, `stem`, `stem_words`, `AmharicStemmer`,
  and `amharic-segmenter --stem`. Stemming also works on words outside the lexicon.
- Function words (`ነው`, `ናቸው`, `ውስጥ` …) are never split.
- Word tokenizer for Ethiopic script: letters, Ethiopic punctuation (`፡ ። ፣ ፤ ፧` …), Ethiopic
  and Arabic numerals, Latin text. No character is ever dropped.
- Sentence splitter for `።`, `፧`, `፨`, `!`, `?` and the old-style `፡፡`.
- Optional morpheme segmentation for nouns and noun phrases: prepositions (`በ ከ ለ የ ስለ`),
  plural, definite article, possessive suffixes, object marker `ን`, conjunctions `ና`/`ም`.
- Three splitting strategies: `lexicon` (default), `rules`, `none`.
- Optional homophone normalisation (`ሐ→ሀ`, `ሠ→ሰ`, `ዐ→አ`, `ፀ→ጸ`).
- Token offsets (`tokenize_spans`), command line interface, typed package (`py.typed`).
- Pronoun contractions (`በኔ`, `ከኛ`, `እንዳንተ`), fused feminine `ዋ` (`ሐኪሟ`), irregular and
  reduplicated-adjective plurals, and `lemma()`.
- Tests from chapter 4 examples (`ጓዳውንና`, `ባለቤቶቹን`, `ሴትዮዋ`).
- `docs/BOOK_COVERAGE.md`: section-by-section record of what the source book covers.
- Seed lexicon built from the examples of *አማርኛ ሠዋሰው* (1963 E.C.).
