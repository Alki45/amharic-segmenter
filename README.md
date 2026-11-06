<div align="center">

# amharic-segmenter

**Sentence and word tokenization, morpheme splitting and stemming for Amharic (አማርኛ)**
as easy as English NLP, built on real grammar rules, with zero dependencies.

[![PyPI](https://img.shields.io/pypi/v/amharic-segmenter.svg)](https://pypi.org/project/amharic-segmenter/)
[![Python](https://img.shields.io/pypi/pyversions/amharic-segmenter.svg)](https://pypi.org/project/amharic-segmenter/)
[![CI](https://github.com/Alki45/amharic-segmenter/actions/workflows/ci.yml/badge.svg)](https://github.com/Alki45/amharic-segmenter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)

[Install](#installation) · [Quickstart](#quickstart) · [Features](#features) · [API](#api-reference) · [CLI](#command-line) · [How it works](#how-it-works) · [Contributing](#contributing)

</div>

> **በአማርኛ:** አማርኛ ጽሑፍን ወደ ዓረፍተ ነገሮችና ቃላት የሚከፋፍል፣ እንዲሁም ቃላትን ወደ ሞርፊሞች
> (`በ`፣ `ከ`፣ `ለ`፣ `ን`፣ `ና`፣ `ዎች`…) የሚሰብር ቀላል የፓይቶን ጥቅል። ለማንኛውም የአማርኛ ቋንቋ ፕሮጀክት ነጻ ነው።

---

## Why this exists

General-purpose tokenizers split on whitespace or learn subwords from data. For Amharic that
leaves two problems:

1. **Ethiopic punctuation is not ASCII.** `።` (full stop), `፣` (comma), `፧` (question mark) and
   the old word separator `፡` are missed or glued to words by generic tools.
2. **Amharic is morphologically rich.** Prepositions, plural, possessives, the object marker
   `ን` and conjunctions are written *attached* to the word, so `ለተማሪዎቻችን` ("for our
   students") is one whitespace token but five units of meaning.

`amharic-segmenter` handles both with transparent, documented rules taken from an Amharic
grammar book, so results are explainable and easy to improve.

## Features

- **NLTK-style API**: `sent_tokenize`, `word_tokenize`, `stem`, `AmharicStemmer`. Works right
  after `pip install`: no model downloads, no setup
- **Stemming** that strips prefixes and suffixes, also for words it has never seen
- **Sentence splitting** on `።`, `፧`, `፨`, `!`, `?` and the old-style `፡፡`
- **Word tokenization** that understands Ethiopic letters, punctuation and numerals
  (`፩፻`), plus Latin text and decimals, and **never drops a character**
- **Morpheme segmentation** of nouns and noun phrases: prepositions `በ ከ ለ የ ስለ`, plural
  (`ች`, `ዎች`), definite article, possessive suffixes, object marker `ን`, conjunctions `ና`/`ም`
- **Precision-first design:** words are only split when the stem is known, so names like
  `ከበደ` and words like `ወንድም` stay intact. An opt-in `rules` mode trades precision for recall
- Handles **pronoun contractions** (`በኔ → በ + እኔ`), **fused feminine forms** (`ሐኪሟ → ሐኪም + ዋ`)
  and **irregular plurals** (`መጻሕፍትን`, `ቃላቶች`), with `lemma()` to get the dictionary form
- **Token offsets** for aligning tokens with the original text
- **Optional normalization** of homophone letters (`ሐ→ሀ`, `ሠ→ሰ`, `ዐ→አ`, `ፀ→ጸ`)
- **Extensible lexicon**: bring your own words, no retraining needed
- **Command line tool**, fully typed (`py.typed`), pure Python, **no dependencies**,
  Python 3.9+

## Installation

```bash
pip install amharic-segmenter
```

## Quickstart

If you have used NLTK on English text, you already know how to use it. Install, import, call:

```python
from amharic_segmenter import word_tokenize, sent_tokenize, stem

text = "ተማሪዎቹ መጻሕፍትን አነበቡ። ከበደና አበበ ለተማሪዎቻቸው ሰጡ።"

sent_tokenize(text)
# ['ተማሪዎቹ መጻሕፍትን አነበቡ።', 'ከበደና አበበ ለተማሪዎቻቸው ሰጡ።']

word_tokenize(text)
# ['ተማሪዎቹ', 'መጻሕፍትን', 'አነበቡ', '።', 'ከበደና', 'አበበ', 'ለተማሪዎቻቸው', 'ሰጡ', '።']

[stem(w) for w in word_tokenize(text)]
# ['ተማሪ', 'መጻሕፍት', 'አነበቡ', '።', 'ከበደ', 'አበበ', 'ተማሪ', 'ሰጡ', '።']
```

Or with a stemmer object, the way you would use `PorterStemmer`:

```python
from amharic_segmenter import AmharicStemmer

stemmer = AmharicStemmer()
stemmer.stem("ተማሪዎችን")                     # 'ተማሪ'
stemmer.stem_words(["ተማሪዎች", "ላሞች"])      # ['ተማሪ', 'ላም']
```

| English (NLTK) | Amharic (this package) |
|----------------|------------------------|
| `nltk.sent_tokenize(text)` | `sent_tokenize(text)` |
| `nltk.word_tokenize(text)` | `word_tokenize(text)` |
| `PorterStemmer().stem(word)` | `AmharicStemmer().stem(word)` or `stem(word)` |
| `nltk.download("punkt")` | **nothing to download**: rules and data ship inside the package |

### More examples

```python
from amharic_segmenter import tokenize, sentence_tokenize

text = "ተማሪዎቹ በከተማ ውስጥ ይኖራሉ። ከበደና አበበ ለተማሪዎቻችን መጽሐፎችን ሰጡ።"

sentence_tokenize(text)
# ['ተማሪዎቹ በከተማ ውስጥ ይኖራሉ።', 'ከበደና አበበ ለተማሪዎቻችን መጽሐፎችን ሰጡ።']

tokenize(text)
# ['ተማሪዎቹ', 'በከተማ', 'ውስጥ', 'ይኖራሉ', '።', 'ከበደና', 'አበበ', 'ለተማሪዎቻችን', 'መጽሐፎችን', 'ሰጡ', '።']

tokenize(text, morphemes=True)
# ['ተማሪ', 'ዎች', 'ው', 'በ', 'ከተማ', 'ውስጥ', 'ይኖራሉ', '።', 'ከበደ', 'ና', 'አበበ',
#  'ለ', 'ተማሪ', 'ዎች', 'ችን', 'መጽሐፍ', 'ች', 'ን', 'ሰጡ', '።']

tokenize(text, morphemes=True, mark_affixes=True)
# ['ተማሪ', '+ዎች', '+ው', 'በ+', 'ከተማ', 'ውስጥ', 'ይኖራሉ', '።', 'ከበደ', '+ና', 'አበበ',
#  'ለ+', 'ተማሪ', '+ዎች', '+ችን', 'መጽሐፍ', '+ች', '+ን', 'ሰጡ', '።']
```

Analyse a single word:

```python
from amharic_segmenter import analyze

analyze("ለተማሪዎቻችን")
# Analysis(word='ለተማሪዎቻችን', prefixes=('ለ',), stem='ተማሪ', suffixes=('ዎች', 'ችን'))
```

Token offsets:

```python
from amharic_segmenter import tokenize_spans

tokenize_spans("ከበደን አየ።")
# [Token(text='ከበደን', start=0, end=4, kind='word'),
#  Token(text='አየ', start=5, end=7, kind='word'),
#  Token(text='።', start=7, end=8, kind='punct')]
```

## Command line

```console
$ amharic-segmenter -m "ለተማሪዎቻችን መጽሐፎችን ሰጡ።"
ለ ተማሪ ዎች ችን መጽሐፍ ች ን ሰጡ ።

$ amharic-segmenter --sentences --json "አበበ መጣ። ከበደ ሄደ።"
["አበበ መጣ።", "ከበደ ሄደ።"]

$ amharic-segmenter --stem "ተማሪዎቹ መጻሕፍትን አነበቡ።"
ተማሪ መጻሕፍት አነበቡ ።

$ echo "ተማሪውንም አየሁ።" | amharic-segmenter -m --mark-affixes
ተማሪ +ው +ን +ም አየሁ ።
```

Run `amharic-segmenter --help` for all options (`--strategy`, `--lexicon`, `--normalize`,
`--no-punct`, `--json`). `python -m amharic_segmenter` works too.

## API reference

### Module-level functions

| Function | Returns | Description |
|----------|---------|-------------|
| `sent_tokenize(text)` | `list[str]` | Sentences (NLTK-style name for `sentence_tokenize`) |
| `word_tokenize(text)` | `list[str]` | Words and punctuation (NLTK-style, same as `tokenize(text)`) |
| `stem(word, *, aggressive=True)` | `str` | Stem of one word. `aggressive=False` leaves words outside the lexicon alone |
| `stem_words(words)` | `list[str]` | Stems of many words |
| `AmharicStemmer().stem(word)` | `str` | Stemmer object, `.stem()` and `.stem_words()` |
| `tokenize(text, *, morphemes=False, include_punct=True, mark_affixes=False)` | `list[str]` | Split text into tokens, optionally down to morphemes |
| `tokenize_spans(text, *, include_punct=True)` | `list[Token]` | Word-level tokens with `start`/`end` offsets and `kind` |
| `sentence_tokenize(text)` | `list[str]` | Split text into sentences |
| `analyze(word)` | `Analysis` | Prefixes, stem and suffixes of one word |
| `split_morphemes(word)` | `list[str]` | Morphemes of one word |
| `lemma(word)` | `str` | Dictionary form of the stem (`መጻሕፍትን → መጽሐፍ`) |
| `normalize_homophones(text)` | `str` | Collapse `ሐ ኀ → ሀ`, `ሠ → ሰ`, `ዐ → አ`, `ፀ → ጸ` (length-preserving) |

### `AmharicTokenizer`

```python
from amharic_segmenter import AmharicTokenizer

tok = AmharicTokenizer(
    lexicon=["መምህር", "ጓደኛ"],   # extra stems that may be split off
    default_lexicon=True,        # include the built-in seed lexicon
    strategy="lexicon",          # "lexicon" | "rules" | "none"
    normalize=False,             # collapse homophone letters first
)

tok.tokenize("መምህራችንን አየሁ።", morphemes=True)
tok.add_words(["ጋዜጣ"])
tok = AmharicTokenizer.from_file("my_words.txt")   # one word per line, '#' comments
```

| `strategy` | Behaviour |
|------------|-----------|
| `"lexicon"` *(default)* | Accept a split only if the stem is in the lexicon. High precision. |
| `"rules"` | Also accept unknown stems of at least `min_stem` letters. Higher recall, more false splits. |
| `"none"` | Never split words into morphemes. |

### `Analysis` and `Token`

- `Analysis(word, prefixes, stem, suffixes)` with `.morphemes` and `.is_split`
- `Token(text, start, end, kind)` where `kind` is `word`, `latin`, `number`, `punct` or `other`

> **Note:** morphemes are *underlying forms*. `ልጆች` becomes `ልጅ + ች` because the plural rule
> changes the stem's last letter, so joining the morphemes does not always give back the
> surface word. Use `tokenize_spans` when you need exact offsets.

## How it works

```
 raw text
    │
    ▼
 ┌──────────────────────────┐   Layer 1: rule-based, always on
 │ sentences and word tokens │   Ethiopic punctuation, numerals, Latin, no loss
 └─────────────┬────────────┘
               │  (optional, morphemes=True)
               ▼
 ┌──────────────────────────┐   Layer 2: morphology
 │ generate candidate splits │   prefixes ← stem → plural → possessive → ን → ና/ም
 │ accept if stem is known   │   lexicon check keeps precision high
 └──────────────────────────┘
```

The morphology layer works on the structure of the Ethiopic script itself: every letter has
seven vowel *orders*, and the plural and possessive rules are defined in terms of them
(`ሰው → ሰዎች`, `አገር → አገራችሁ`). The rules are listed with book references in
[`docs/GRAMMAR_RULES.md`](docs/GRAMMAR_RULES.md).

The rules are based on the grammar book *አማርኛ ሠዋሰው* (1963 E.C.).

## How it relates to other Amharic tools

| Project (PyPI) | Approach | Good for |
|----------------|----------|----------|
| **`amharic-segmenter`** (this package) | Grammar rules from a printed grammar book, NLTK-style API | Sentence and word splitting, morpheme splitting, stemming, explainable output |
| `amharic-tokenizer` | BPE-like merges learned from a corpus | Subword vocabularies for training language models |
| `amseg` | Rule-based sentence and word splitter, with normalizer and romanizer | Sentence/word splitting and transliteration |

They solve different problems and can be used together, for example `amharic-segmenter` for
sentences and stems and a trained BPE model for model vocabularies.

## Current scope and limitations

This is an early release (`0.1`, alpha). Please read this before using it in production:

- Only **printed pages 7-110** of the source book have been used so far (chapters 1-5 and the
  start of chapter 6; the punctuation chapter is still missing). See [`docs/BOOK_COVERAGE.md`](docs/BOOK_COVERAGE.md) for exactly what is
  and is not covered, e.g. the book's chapter on punctuation.
- Stemming is a **noun-oriented** suffix stripper, like a light English stemmer. Verbs are
  left alone rather than guessed. Prefixes (`በ ከ ለ የ`) are only stripped when the rest is a
  known word, so unknown words lose suffixes only. For unknown nouns it can pick the wrong stem when the
  last letter is ambiguous (`ጋዜጦች` could come from `ጋዜጣ` or `ጋዜጥ`).
- Morphology covers **nouns and noun phrases**. **Verb morphology is not implemented yet.**
- The built-in lexicon is a small seed. Unknown stems are left unsplit in the default mode,
  so coverage grows as the lexicon grows. Add your own words or send a pull request.
- Some forms are ambiguous without context (a final `ም` can be a conjunction or part of the
  word, as in `ወንድም`). The lexicon resolves most cases, not all.
- Rules reflect one grammar book. Modern usage and dialects may differ; native-speaker
  review is very welcome.

## Roadmap

- [ ] Punctuation rules from chapter 7 of the source book (pages still to be added)
- [ ] Verb morphology (agreement, tense, negation, relative `የ…`) from an additional source
- [ ] Larger open lexicon and a test corpus of annotated sentences
- [ ] Reduplicated plurals and internal plurals as rules
- [ ] Subword-vocabulary export for use with ML tokenizers
- [ ] Evaluation scripts against annotated Amharic data

## Contributing

Contributions are very welcome, especially from Amharic speakers and linguists. The easiest
first contribution is adding words to
[`src/amharic_segmenter/data/lexicon.txt`](src/amharic_segmenter/data/lexicon.txt).
See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, rules for adding grammar rules, and the pull
request checklist.

```bash
git clone https://github.com/Alki45/amharic-segmenter.git
cd amharic-segmenter
pip install -e ".[dev]"
pytest
```

## Citation

If you use this package in research, please cite it:

```bibtex
@software{amharic_segmenter,
  title  = {amharic-segmenter: Sentence, word and morpheme tokenization for Amharic},
  author = {Ali Kibret Muhamed},
  year   = {2026},
  url    = {https://github.com/Alki45/amharic-segmenter}
}
```

## License

[MIT](LICENSE). The grammar rules are re-implemented in original code; the source book is
credited above and its text is not redistributed.
