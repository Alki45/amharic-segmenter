"""Rule-based morphological segmentation for Amharic nouns and noun phrases.

The rules implemented here come from the grammar book *አማርኛ ሠዋሰው* (1963 E.C.):
prepositions that attach to the following word, the plural, the definite
article and possessive suffixes, the object marker ``ን`` and the conjunctions
``ና`` / ``ም``.  See ``docs/GRAMMAR_RULES.md`` for the rule-by-rule mapping.

A candidate split is only accepted when the remaining *stem* is trustworthy:
either it is in the lexicon (default, high precision) or, in the opt-in
``"rules"`` strategy, it is at least ``min_stem`` letters long.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Set
from dataclasses import dataclass

from .charset import KAEB, RABI, SABI, SADIS, fidel_order, is_wa_form, with_order

# Prefixes written together with the word that follows them.
PREFIXES: tuple[str, ...] = ("ስለ", "በ", "ከ", "ለ", "የ")
MAX_PREFIXES = 2

# Suffix slots, from the stem outward:  plural -> possessive/definite -> ን -> ና/ም
CONJUNCTIONS: tuple[str, ...] = ("ና", "ም")
OBJECT_MARKER = "ን"
POSSESSIVE_DEFINITE: tuple[str, ...] = ("ቸው", "ችሁ", "ችን", "ው", "ዋ", "ህ", "ሽ", "ዬ")
# Suffixes before which the stem's last letter surfaces in the 'a' order
# (አገር + ችሁ -> አገራችሁ, ተማሪዎች + ችን -> ተማሪዎቻችን).
_LINKING: tuple[str, ...] = ("ቸው", "ችሁ", "ችን")

# Prepositions fuse with pronouns that start with እ: በ + እኔ -> በኔ, ከ + እኛ -> ከኛ,
# እንደ + አንተ -> እንዳንተ.
_CONTRACTING_PRONOUNS: tuple[str, ...] = ("እኔ", "እኛ", "እሱ", "እሷ", "እነሱ", "እርሱ", "እርሷ", "እናንተ")
CONTRACTION_PREFIXES: tuple[str, ...] = ("በ", "ከ", "ለ", "የ", "እንደ")


def _build_contractions() -> dict[str, tuple[str, str]]:
    table = {}
    for prefix in CONTRACTION_PREFIXES:
        for pronoun in _CONTRACTING_PRONOUNS:
            table[prefix + pronoun[1:]] = (prefix, pronoun)
    for pronoun in ("አንተ", "አንቺ"):
        table["እንዳ" + pronoun[1:]] = ("እንደ", pronoun)
    return table


CONTRACTIONS = _build_contractions()

_ETHIOPIC_WORD = re.compile(r"^[\u1200-\u135A]+$")


@dataclass(frozen=True)
class Analysis:
    """Result of segmenting one word.

    ``morphemes`` are normalised morphs (underlying forms), so concatenating
    them does not always reproduce the surface word (e.g. ልጆች -> ልጅ + ች).
    """

    word: str
    prefixes: tuple[str, ...] = ()
    stem: str = ""
    suffixes: tuple[str, ...] = ()

    @property
    def morphemes(self) -> list[str]:
        return [*self.prefixes, self.stem, *self.suffixes]

    @property
    def is_split(self) -> bool:
        return bool(self.prefixes or self.suffixes)


def _opt(word: str, suffixes: tuple[str, ...]) -> Iterator[tuple[str, str | None]]:
    yield word, None
    for s in suffixes:
        if len(word) > len(s) and word.endswith(s):
            yield word[: -len(s)], s


def _opt_possessive(word: str) -> Iterator[tuple[str, str | None, bool]]:
    """Possessive / definite-article slot, including fused surface forms.

    The third item is ``True`` for *fused* forms (ሐኪሟ, ልጁ), which only nouns have.
    They are accepted for known stems only, so verbs such as አየሁ are never touched.
    """
    yield word, None, False
    for s in POSSESSIVE_DEFINITE:
        if len(word) > len(s) and word.endswith(s):
            rest = word[: -len(s)]
            yield rest, s, False
            if s in _LINKING and rest:
                last = rest[-1]
                if fidel_order(last) == RABI:  # አገራችሁ -> አገር, ተማሪዎቻችን -> ተማሪዎች
                    yield rest[:-1] + with_order(last, SADIS), s, False
    # feminine 'ዋ' fused into the last letter (labialised form): ሐኪሟ -> ሐኪም + ዋ
    if len(word) >= 2 and is_wa_form(word[-1]):
        yield word[:-1] + chr(ord(word[-1]) - 2), "ዋ", True
    # masculine definite 'ኡ' fused into the last letter: ልጁ -> ልጅ, ተማሪዎቹ -> ተማሪዎች
    if len(word) >= 2 and fidel_order(word[-1]) == KAEB:
        yield word[:-1] + with_order(word[-1], SADIS), "ው", True


def _opt_plural(word: str) -> Iterator[tuple[str, str | None]]:
    """Plural slot (the 1948 spelling convention described in the book)."""
    yield word, None
    if len(word) > 2 and word.endswith("ዎች"):
        yield word[:-2], "ዎች"
    if len(word) >= 2 and word.endswith("ች"):
        stem0, prev = word[:-2], word[-2]
        if fidel_order(prev) == SABI:
            for order in (SADIS, RABI):  # ሰዎች -> ሰው, ጌቶች -> ጌታ
                yield stem0 + with_order(prev, order), "ች"
            yield stem0 + prev, "ች"  # በቅሎች -> በቅሎ


def _suffix_variants(word: str) -> Iterator[tuple[str, tuple[str, ...], bool]]:
    for w1, conj in _opt(word, CONJUNCTIONS):
        for w2, obj in _opt(w1, (OBJECT_MARKER,)):
            for w3, pos, fused in _opt_possessive(w2):
                for w4, plural in _opt_plural(w3):
                    yield w4, tuple(x for x in (plural, pos, obj, conj) if x), fused


def _prefix_variants(stem: str, depth: int = MAX_PREFIXES) -> Iterator[tuple[tuple[str, ...], str]]:
    yield (), stem
    if depth == 0:
        return
    for p in PREFIXES:
        if len(stem) > len(p) and stem.startswith(p):
            for rest_prefixes, rest in _prefix_variants(stem[len(p):], depth - 1):
                yield (p, *rest_prefixes), rest


def analyze_word(
    word: str,
    lexicon: Set[str],
    strategy: str = "lexicon",
    min_stem: int = 2,
) -> Analysis:
    """Segment ``word`` into prefixes, a stem and suffixes.

    ``strategy``:
      * ``"lexicon"`` - accept a split only if the stem is a known word.
      * ``"rules"``   - also accept any stem of at least ``min_stem`` letters
        (higher recall, more false splits).
      * ``"none"``    - never split.
    """
    unsplit = Analysis(word, (), word, ())
    if strategy == "none" or word in lexicon or not _ETHIOPIC_WORD.match(word):
        return unsplit

    # Ranking of candidate analyses:
    #  * a stem found in the lexicon always beats an unknown one; among those,
    #    fewer affixes and then the longer stem win (conservative);
    #  * for unknown stems ("rules" strategy) avoid guessing prefixes, then peel
    #    as many suffixes as possible (e.g. ቸው rather than only ው).
    best: Analysis | None = None
    best_key: tuple[int, ...] | None = None
    for stem_candidate, suffixes, fused in _suffix_variants(word):
        contraction = CONTRACTIONS.get(stem_candidate)
        if contraction is not None and contraction[1] in lexicon:
            prefix, pronoun = contraction
            key = (0, 1 + len(suffixes), -len(pronoun))
            if best_key is None or key < best_key:
                best_key, best = key, Analysis(word, (prefix,), pronoun, suffixes)
        for prefixes, stem in _prefix_variants(stem_candidate):
            if not (prefixes or suffixes):
                continue
            known = stem in lexicon
            if fused and not known:
                continue  # fused forms are only trusted for words in the lexicon
            if not (known or (strategy == "rules" and len(stem) >= min_stem)):
                continue
            if known:
                key: tuple[int, ...] = (0, len(prefixes) + len(suffixes), -len(stem))
            else:
                key = (1, len(prefixes), -len(suffixes), len(stem))
            if best_key is None or key < best_key:
                best_key, best = key, Analysis(word, prefixes, stem, suffixes)
    return best or unsplit
