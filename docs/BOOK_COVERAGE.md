# Coverage of the source book

Source: **አማርኛ ሠዋሰው** (1963 E.C.), photographed pages. This file records, section by
section, what has been checked and what has not, so nothing is silently skipped.

**Pages available so far: printed pages 7-110** (two PDFs: pp. 7-60 and pp. 61-110).
The book has seven chapters, judging by the headings: 1 parts of the sentence, 2 number,
3 gender, 4 linking of clauses, 5 essay writing (*ድርሰት*), 6 understanding the topic
(*አርእስትን መረዳት*, begins p. 105) and 7 punctuation (*ሥርዓተ ነጥብ*, begins around p. 154).
Pages 111 onward are **not** provided, so the rest of chapter 6 and all of chapter 7 are
**not covered**. The book has **no chapter on verb morphology**, so that would need
another source.

Legend: ✅ implemented and tested · 🟡 partly / only through the lexicon · ➖ grammar of
sentence structure, no effect on tokenization · ❌ not in the provided pages

| Printed pages | Section | Topic | Status |
|---------------|---------|-------|--------|
| 7-9 | መግቢያ | Preface | ➖ |
| 10-12 | ምዕራፍ 1 | The five roles of a noun in a sentence | ➖ |
| 12-14 | 1.1 ባለቤት | Subject; pronouns as subject | ➖ |
| 14-15 | 1.1.2 | Subject-agreement suffixes and prefixes **on verbs** (`ሁ ህ ሽ …`, `አ ት ይ እን`) | ❌ verbs not implemented |
| 16-17 | 1.1.3-1.1.5 | Dependent clauses, infinitive (`መ-`/`ማ-`), compound subjects | ➖ / ❌ verbs |
| 18-28 | 1.2 ቀጥተኛ ተሳቢ | Direct object: marker `ን`, when it is required or omitted | ✅ `ን` splitting · ➖ when to use it |
| 24-26 | 1.2.2 | Definite article `ው`/`ዋ`, demonstratives (`ይህ ይህች ያ ያች እነዚህ እነዚያ`), possessive suffixes | ✅ (`ክ` variant of `ህ`, p. 26, ❌ unclear in photo) |
| 27 | 1.2.2 | Pronouns taking `ን` (`እኔን እሱን እናንተን አንቺን`) | ✅ |
| 29-33 | 1.3 የመስተዋድድ ተጎኝ | Prepositions `በ ከ ለ እንደ የ ስለ`; `የ` in relative clauses | ✅ prefixes · 🟡 `እንደ`/`ወደ` are written as separate words |
| 30 | 1.3 | Pronoun contractions `በኔ በሱ ከኛ እንዳንተ` | ✅ added in 0.1 |
| 33-35 | 1.4 ተጣማሪ | Complements | ➖ |
| 35-38 | 1.5 መሙያ | Adverbial fillers | ➖ |
| 39-41 | 2 ቁጥር, 2.1 | Plural `ች`/`ዎች` and the 1948 spelling rules (ሀ, ለ, ሐ) | ✅ |
| 42-44 | 2.2 | Geez-origin plurals (`መጽሐፍ → መጻሕፍት` …), double plurals (`ቃላቶች`) | 🟡 table of 24 clear entries; others skipped |
| 44-47 | 2.3 | Number agreement noun-verb-adjective | ➖ |
| 47-48 | 2.3.4 | Adjectives with reduplicated plural (`ትልቅ → ትልልቅ`) | 🟡 8 listed adjectives; no general rule |
| 48-50 | exercises | Sentences for practice | ➖ (used as test ideas) |
| 51-53 | 3 ፆታ | Gender: feminine `ዋ`, fused forms such as `ሐኪሟ` | ✅ added in 0.1 |
| 53-56 | 3.1 | Gender agreement errors, `ች` on verbs | ➖ / ❌ verbs |
| 57-60 | 4 የሐረግ ዝምድና | Conjunction `ና` between equal parts | ✅ attachment · ➖ when to use it |
| 61-62 | 4.1-4.2 | Conjunction `ና` and independent vs dependent clauses | ✅ `ና` (suffix order checked on `ጓዳውንና`, `ባለቤቶቹን`) · ➖ clauses |
| 63-75 | exercises | Practice sentences for chapters 1-4 | ➖ (used as test ideas only) |
| 76-104 | 5 ድርሰት | How to write an essay: paragraphs, topic, sentence quality | ➖ |
| 105-110 | 6 አርእስትን መረዳት | Understanding the topic; a sample reading passage | ➖ |
| 111-153 | rest of 6 | (not provided) | ❌ |
| 154+ | 7 ሥርዓተ ነጥብ | Punctuation marks: `፡ ፣ ፤ ። ፧ !`, quotation marks, ellipsis | ❌ **not provided** |

## How pages 61-110 were checked

These pages are scans without a text layer and no Amharic OCR was available, so they were
read visually: every page was looked at as a contact sheet to find headings and section
types, and the pages that contain grammar rules (61-65 and the chapter openings 76 and 105)
were read in full. The exercise and essay pages were skimmed, not read word for word.

## Reading limits of photographed pages

- A few characters are unclear in the photos (creases, shadows, marginal pen marks).
  Rules and examples were only used where the text was clear enough to read.
- The irregular-plural table and the `ክ` possessive variant need a second pair of eyes.
- Pen annotations on the pages were ignored.

## What would complete the coverage

1. Printed pages 111 to the end of the book, especially chapter 7 on punctuation.
2. A native-speaker review of `docs/GRAMMAR_RULES.md` and
   `src/amharic_segmenter/data/irregular_plurals.tsv`.
