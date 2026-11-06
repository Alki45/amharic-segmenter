# Contributing to amharic-segmenter

Thank you for helping Amharic get better tooling! All kinds of contributions are welcome:
bug reports, new grammar rules, lexicon words, test sentences, documentation and
native-speaker review.

## Quick start

```bash
git clone https://github.com/Alki45/amharic-segmenter.git
cd amharic-segmenter
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Ways to contribute

### 1. Add words to the lexicon (easiest)
Add stems (nouns, names, pronouns, …) to `src/amharic_segmenter/data/lexicon.txt`, one per
line, in the section that fits. A word in the lexicon is never split, and other words can be
split down to it (e.g. `ተማሪዎች → ተማሪ + ዎች`).

### 2. Report a wrong split
Open an issue with the word, the output you got, the output you expected and, if you can,
the grammar rule or a source that supports it.

### 3. Add or fix a grammar rule
1. Find the rule in a grammar source and note the reference (book, page).
2. Implement it in `src/amharic_segmenter/morphology.py`. Rules are small generator
   functions (`_opt_plural`, `_opt_possessive`, …) that yield candidate splits; the lexicon
   decides which candidate is accepted.
3. Add tests in `tests/test_morphology.py` with real example words, including words that
   must **not** be split.
4. Document the rule in `docs/GRAMMAR_RULES.md`.

### 4. Native-speaker review
If you speak Amharic, reviewing `docs/GRAMMAR_RULES.md` and the tests is very valuable.
Open an issue titled "Review: …" with corrections.

## Pull request checklist
- [ ] `pytest` passes and new behaviour has tests
- [ ] `ruff check .` is clean
- [ ] Public functions have docstrings
- [ ] `CHANGELOG.md` has an entry under *Unreleased*
- [ ] Grammar changes are referenced in `docs/GRAMMAR_RULES.md`

## Guidelines
- Keep the package dependency-free.
- Prefer precision over recall by default: a missed split is better than a wrong split.
- Be kind and respectful. Disagreements about grammar are normal; please bring sources.
- Do not copy long passages from copyrighted books. Describe rules in your own words and
  use short example words.
