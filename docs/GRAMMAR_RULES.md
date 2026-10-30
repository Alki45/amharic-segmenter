# Grammar rules implemented

All rules come from the grammar book **አማርኛ ሠዋሰው** (1963 E.C.). Page numbers are the
printed page numbers of the edition used. Rules are re-implemented in original code and
short example words are used as tests; nothing is copied from the book at length.

Terminology: *order* = the vowel form of a letter (ግዕዝ, ካዕብ, ሣልስ, ራብዕ, ሃምስ, ሳድስ, ሳብዕ).

| # | Rule | Book (printed pages) | Implemented in | Examples |
|---|------|----------------------|----------------|----------|
| 1 | Words are separated by spaces or `፡`; sentences end with `።` (also `፡፡` in older print) | passim | `tokenizer.py` | `አበበ፡ከበደን፡አየ፡፡` |
| 2 | Direct-object marker `ን` attaches to the last word of the object | 19-23 | `_suffix_variants` | `ከበደን`, `ይህን`, `እሱን` |
| 3 | Definite article / possessive 3rd person: masculine `ው`/`ኡ`, feminine `ዋ`; `ኡ` fuses into the last letter | 24, 26 | `_opt_possessive` | `ተማሪው`, `ልጁ → ልጅ + ው` |
| 4 | Possessive suffixes `ዬ ህ ሽ ው ዋ ችን ችሁ ቸው` | 25-27 | `_opt_possessive` | `ቤትህን`, `ልብስሽን` |
| 5 | Before `ችን ችሁ ቸው` the last letter surfaces in the *ራብዕ* (`a`) order | 26-27 | `_opt_possessive` | `አገራችሁን → አገር`, `ችግራቸውን → ችግር` |
| 6 | Plural `ች`: a word ending in *ራብዕ* or *ሳድስ* changes its last letter to *ሳብዕ* and adds `ች` | 41 | `_opt_plural` | `ሰው → ሰዎች`, `ፈረስ → ፈረሶች`, `በር → በሮች` |
| 7 | Plural `ች`: a word ending in *ሳብዕ* just adds `ች` | 41 | `_opt_plural` | `በቅሎ → በቅሎች` |
| 8 | Plural `ዎች`: a word ending in *ካዕብ*, *ሣልስ* or *ሃምስ* adds `ዎች` unchanged | 41 | `_opt_plural` | `ክፉዎች`, `ተማሪዎች`, `ገበሬዎች` |
| 9 | Prepositions `በ ከ ለ የ ስለ` are written together with the following word | 29-34 | `_prefix_variants` | `በከተማ`, `ለተማሪ` |
| 10 | Conjunctions `ና` ("and") and `ም` ("also") attach to the end of a word, after `ን` | 57-60 | `_suffix_variants` | `ከበደና`, `ተማሪውንም` |
| 11 | Feminine `ዋ`, also fused into the last letter in its labialised form | 51-53 | `_opt_possessive` | `ድንጋይዋ`, `ሐኪሟ → ሐኪም + ዋ` |
| 12 | Prepositions fuse with pronouns that start with `እ` | 30 | `CONTRACTIONS` | `በኔ → በ + እኔ`, `ከኛ`, `እንዳንተ → እንደ + አንተ` |
| 13 | Geez-origin irregular plurals and reduplicated adjective plurals (lexicon table) | 42-44, 47-48 | `data/irregular_plurals.tsv` | `መጻሕፍትን`, `ቃላቶች`, `ትልልቅ` |

Suffix order, from the stem outward: **plural → possessive/definite → `ን` → `ና`/`ም`**,
for example `ለተማሪዎቻችንን = ለ + ተማሪ + ዎች + ችን + ን`.

## Design decisions

- **Morphemes are underlying forms.** `ልጆች` is returned as `ልጅ + ች` because rule 6 changes
  the last letter of the stem. Concatenating morphemes does not always reproduce the word.
- **Precision first.** A split is accepted only if the stem is in the lexicon
  (`strategy="lexicon"`). This prevents cutting `ወንድም`, `ሐኪም`, `ላም` (end in `ም`) or the
  name `ከበደ` (starts with `ከ`).
- **`strategy="rules"`** also accepts unknown stems of 2+ letters. It prefers analyses
  without guessed prefixes and with the most suffixes. Useful for exploration, noisier.

## Not implemented yet

- Verb morphology (subject/object agreement, tense, negation `አ…ም`, relative `የ…`). The
  source book has no chapter on it, so another grammar source is needed.
- General rules for reduplicated adjective plurals and internal plurals; today they work
  only for the entries listed in `data/irregular_plurals.tsv`.
- Loanword plurals and irregular forms discussed in the book's section on foreign nouns.
- Feminine `ች` on verbs, gender agreement, and the `ክ` variant of the possessive `ህ`.
- Everything after printed page 110 (see `BOOK_COVERAGE.md`), including the punctuation chapter.
- Disambiguating `ም`/`ና`/`ን` using sentence context.

Corrections and additions are very welcome: see `CONTRIBUTING.md`.
