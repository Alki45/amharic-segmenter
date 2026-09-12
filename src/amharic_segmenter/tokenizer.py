"""Word, sentence and morpheme tokenization for Amharic."""
from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import NamedTuple

from .morphology import Analysis, analyze_word
from .normalize import normalize_homophones

_STRATEGIES = ("lexicon", "rules", "none")

# One alternation, tried in order.  Every non-space character belongs to
# exactly one token, so nothing is ever silently dropped.
_TOKEN_RE = re.compile(
    r"(?P<word>[\u1200-\u135A\u135D-\u135F\u1380-\u138F]+)"
    r"|(?P<ethnum>[\u1369-\u137C]+)"
    r"|(?P<latin>[A-Za-z\u00C0-\u024F]+(?:['\u2019\-][A-Za-z\u00C0-\u024F]+)*)"
    r"|(?P<number>\d+(?:[.,]\d+)*)"
    r"|(?P<punct>\u1361\u1361|[\u1360-\u1368]|[^\w\s])"
    r"|(?P<other>\S)"
)
_KINDS = {
    "word": "word",
    "ethnum": "number",
    "latin": "latin",
    "number": "number",
    "punct": "punct",
    "other": "other",
}

# Sentence terminators: ። ፧ ፨ ! ? and the old-style double word-separator ፡፡
_TERMINATOR_RE = re.compile(r"(?:\u1361\u1361|[\u1362\u1367\u1368!?]+)[\u00BB\u201D\"')\]]*")


class Token(NamedTuple):
    """A token with its character offsets in the (normalised) input text."""

    text: str
    start: int
    end: int
    kind: str  # "word", "latin", "number", "punct" or "other"


def _parse_lexicon(text: str) -> Iterator[str]:
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


@lru_cache(maxsize=1)
def load_irregular_plurals() -> tuple[tuple[str, str], ...]:
    """Load (singular, plural) pairs of irregular plurals shipped with the package."""
    resource = resources.files("amharic_segmenter") / "data" / "irregular_plurals.tsv"
    pairs = []
    for line in _parse_lexicon(resource.read_text(encoding="utf-8")):
        parts = line.split("\t")
        if len(parts) == 2:
            pairs.append((parts[0].strip(), parts[1].strip()))
    return tuple(pairs)


@lru_cache(maxsize=1)
def load_default_lexicon() -> frozenset:
    """Load the seed lexicon (plus irregular plural forms) shipped with the package."""
    resource = resources.files("amharic_segmenter") / "data" / "lexicon.txt"
    words = set(_parse_lexicon(resource.read_text(encoding="utf-8")))
    for singular, plural in load_irregular_plurals():
        words.update((singular, plural))
    return frozenset(words)


class AmharicTokenizer:
    """Configurable Amharic tokenizer.

    Parameters
    ----------
    lexicon:
        Extra stems (an iterable of words) that are allowed to be split off.
    default_lexicon:
        Include the seed lexicon that ships with the package.
    strategy:
        ``"lexicon"`` (default, high precision), ``"rules"`` (higher recall) or
        ``"none"`` (never split morphemes).
    normalize:
        Collapse homophone letters (ሐ->ሀ, ሠ->ሰ, ዐ->አ, ፀ->ጸ) before tokenizing.
    min_stem:
        Minimum stem length (in letters) for the ``"rules"`` strategy.
    """

    def __init__(
        self,
        lexicon: Iterable[str] | None = None,
        *,
        default_lexicon: bool = True,
        strategy: str = "lexicon",
        normalize: bool = False,
        min_stem: int = 2,
    ) -> None:
        if strategy not in _STRATEGIES:
            raise ValueError(f"strategy must be one of {_STRATEGIES}, got {strategy!r}")
        self.strategy = strategy
        self.normalize = normalize
        self.min_stem = min_stem
        words = set(load_default_lexicon()) if default_lexicon else set()
        if lexicon is not None:
            words.update(w.strip() for w in lexicon if w.strip())
        self._lexicon = frozenset(self._prep(w) for w in words)
        self._irregular: dict[str, str] = (
            {self._prep(pl): self._prep(sg) for sg, pl in load_irregular_plurals()}
            if default_lexicon else {}
        )
        self._cache: dict[str, Analysis] = {}
        self._rules_cache: dict[str, Analysis] = {}

    # -- helpers ---------------------------------------------------------
    def _prep(self, text: str) -> str:
        return normalize_homophones(text) if self.normalize else text

    @classmethod
    def from_file(cls, path: str | Path, **kwargs) -> AmharicTokenizer:
        """Build a tokenizer with extra stems read from a UTF-8 file."""
        words = list(_parse_lexicon(Path(path).read_text(encoding="utf-8")))
        return cls(lexicon=words, **kwargs)

    def add_words(self, words: Iterable[str]) -> None:
        """Add stems to the lexicon of this tokenizer."""
        self._lexicon = self._lexicon | {self._prep(w.strip()) for w in words if w.strip()}
        self._cache.clear()
        self._rules_cache.clear()

    @property
    def lexicon(self) -> frozenset:
        return self._lexicon

    # -- morphology ------------------------------------------------------
    def analyze(self, word: str) -> Analysis:
        """Segment one word into prefixes, stem and suffixes."""
        word = self._prep(word)
        cached = self._cache.get(word)
        if cached is None:
            cached = analyze_word(word, self._lexicon, self.strategy, self.min_stem)
            self._cache[word] = cached
        return cached

    def split_morphemes(self, word: str) -> list[str]:
        """Return the morphemes of one word, e.g. ``['ለ', 'ተማሪ', 'ዎች']``."""
        return self.analyze(word).morphemes

    def stem(self, word: str, *, aggressive: bool = True) -> str:
        """Strip prefixes and suffixes and return the stem (like ``PorterStemmer.stem``).

        Known words are segmented with the lexicon.  With ``aggressive=True`` (the
        default) a word that is not in the lexicon still loses its suffixes using
        the grammar rules alone, so the stemmer works on any noun, as English
        stemmers do.  Use ``aggressive=False`` to leave unknown words untouched.
        """
        word = self._prep(word)
        analysis = self.analyze(word)
        if not analysis.is_split and aggressive and self.strategy == "lexicon":
            analysis = self._rules_cache.get(word)  # type: ignore[assignment]
            if analysis is None:
                analysis = analyze_word(word, self._lexicon, "rules", self.min_stem)
                self._rules_cache[word] = analysis
        return analysis.stem

    def lemma(self, word: str) -> str:
        """Dictionary form of the stem: ``መጻሕፍትን -> መጽሐፍ``, ``ተማሪዎች -> ተማሪ``."""
        stem = self.analyze(word).stem
        return self._irregular.get(stem, stem)

    # -- tokenization ----------------------------------------------------
    def tokenize_spans(self, text: str, *, include_punct: bool = True) -> list[Token]:
        """Word-level tokens with offsets (into the normalised text)."""
        text = self._prep(text)
        tokens = []
        for m in _TOKEN_RE.finditer(text):
            kind = _KINDS[m.lastgroup]  # type: ignore[index]
            if kind == "punct" and not include_punct:
                continue
            tokens.append(Token(m.group(), m.start(), m.end(), kind))
        return tokens

    def tokenize(
        self,
        text: str,
        *,
        morphemes: bool = False,
        include_punct: bool = True,
        mark_affixes: bool = False,
    ) -> list[str]:
        """Split text into tokens.

        With ``morphemes=True`` every Amharic word is further split into its
        prefixes, stem and suffixes.  ``mark_affixes=True`` writes prefixes as
        ``በ+`` and suffixes as ``+ን`` so the two can be told apart.
        """
        out: list[str] = []
        for tok in self.tokenize_spans(text, include_punct=include_punct):
            if morphemes and tok.kind == "word":
                a = self.analyze(tok.text)
                if mark_affixes:
                    out.extend(p + "+" for p in a.prefixes)
                    out.append(a.stem)
                    out.extend("+" + s for s in a.suffixes)
                else:
                    out.extend(a.morphemes)
            else:
                out.append(tok.text)
        return out

    def sentence_tokenize(self, text: str) -> list[str]:
        """Split text into sentences on ። ፧ ፨ ! ? and ፡፡."""
        sentences: list[str] = []
        start = 0
        for m in _TERMINATOR_RE.finditer(text):
            end = m.end()
            if end == len(text) or text[end].isspace():
                chunk = text[start:end].strip()
                if chunk:
                    sentences.append(chunk)
                start = end
        tail = text[start:].strip()
        if tail:
            sentences.append(tail)
        return sentences


class AmharicStemmer:
    """Stemmer with the familiar NLTK shape: ``AmharicStemmer().stem("ተማሪዎችን")``."""

    def __init__(self, tokenizer: AmharicTokenizer | None = None, *, aggressive: bool = True) -> None:
        self.tokenizer = tokenizer or _default_tokenizer()
        self.aggressive = aggressive

    def stem(self, word: str) -> str:
        """Return the stem of one word."""
        return self.tokenizer.stem(word, aggressive=self.aggressive)

    def stem_words(self, words: Iterable[str]) -> list[str]:
        """Return the stems of many words."""
        return [self.stem(w) for w in words]


@lru_cache(maxsize=1)
def _default_tokenizer() -> AmharicTokenizer:
    return AmharicTokenizer()


def word_tokenize(text: str) -> list[str]:
    """Split text into words and punctuation (like ``nltk.word_tokenize``)."""
    return _default_tokenizer().tokenize(text)


def sent_tokenize(text: str) -> list[str]:
    """Split text into sentences (like ``nltk.sent_tokenize``)."""
    return _default_tokenizer().sentence_tokenize(text)


def stem(word: str, *, aggressive: bool = True) -> str:
    """Stem of one word, using the default tokenizer."""
    return _default_tokenizer().stem(word, aggressive=aggressive)


def stem_words(words: Iterable[str], *, aggressive: bool = True) -> list[str]:
    """Stems of many words, using the default tokenizer."""
    return [stem(w, aggressive=aggressive) for w in words]


def tokenize(
    text: str,
    *,
    morphemes: bool = False,
    include_punct: bool = True,
    mark_affixes: bool = False,
) -> list[str]:
    """Tokenize ``text`` with the default tokenizer."""
    return _default_tokenizer().tokenize(
        text, morphemes=morphemes, include_punct=include_punct, mark_affixes=mark_affixes
    )


def tokenize_spans(text: str, *, include_punct: bool = True) -> list[Token]:
    """Tokens with offsets, using the default tokenizer."""
    return _default_tokenizer().tokenize_spans(text, include_punct=include_punct)


def sentence_tokenize(text: str) -> list[str]:
    """Split ``text`` into sentences with the default tokenizer."""
    return _default_tokenizer().sentence_tokenize(text)


def analyze(word: str) -> Analysis:
    """Morphological analysis of a single word."""
    return _default_tokenizer().analyze(word)


def split_morphemes(word: str) -> list[str]:
    """Morphemes of a single word, using the default tokenizer."""
    return _default_tokenizer().split_morphemes(word)


def lemma(word: str) -> str:
    """Dictionary form of the stem of ``word``, using the default tokenizer."""
    return _default_tokenizer().lemma(word)
