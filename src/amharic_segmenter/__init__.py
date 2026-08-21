"""amharic-segmenter: sentence, word and morpheme tokenization for Amharic (አማርኛ)."""
from __future__ import annotations

from ._version import __version__
from .morphology import Analysis
from .normalize import normalize_homophones
from .tokenizer import (
    AmharicStemmer,
    AmharicTokenizer,
    Token,
    analyze,
    lemma,
    sent_tokenize,
    sentence_tokenize,
    split_morphemes,
    stem,
    stem_words,
    tokenize,
    tokenize_spans,
    word_tokenize,
)

__all__ = [
    "AmharicStemmer",
    "AmharicTokenizer",
    "Analysis",
    "Token",
    "__version__",
    "analyze",
    "lemma",
    "normalize_homophones",
    "sent_tokenize",
    "sentence_tokenize",
    "split_morphemes",
    "stem",
    "stem_words",
    "tokenize",
    "tokenize_spans",
    "word_tokenize",
]
