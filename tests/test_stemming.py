"""NLTK-style API: word_tokenize, sent_tokenize, stem, AmharicStemmer."""
import io
from contextlib import redirect_stdout

import pytest

from amharic_segmenter import (
    AmharicStemmer,
    AmharicTokenizer,
    sent_tokenize,
    stem,
    stem_words,
    word_tokenize,
)
from amharic_segmenter.cli import main


def test_word_and_sentence_tokenize():
    assert word_tokenize("አበበ ከበደን አየ።") == ["አበበ", "ከበደን", "አየ", "።"]
    assert sent_tokenize("አበበ መጣ። ከበደ ሄደ።") == ["አበበ መጣ።", "ከበደ ሄደ።"]


@pytest.mark.parametrize(
    "word, expected",
    [
        ("ተማሪዎችን", "ተማሪ"),
        ("ለተማሪዎቻችን", "ተማሪ"),
        ("ተማሪዎቹ", "ተማሪ"),
        ("ቤቶቻቸው", "ቤት"),
        ("ሐኪሞቻቸው", "ሐኪም"),
        ("ትምህርቱን", "ትምህርት"),
        ("አገራችን", "አገር"),
        ("ሰዎች", "ሰው"),
        ("መጻሕፍትን", "መጻሕፍት"),
        ("ተማሪ", "ተማሪ"),
    ],
)
def test_stem_known_nouns(word, expected):
    assert stem(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("አሠሪዎች", "አሠሪ"),       # unknown noun: plural stripped by the rules alone
        ("መኪናዋ", "መኪና"),         # unknown noun: feminine suffix
        ("አሠሪዎችንም", "አሠሪ"),
    ],
)
def test_stem_unknown_nouns_with_rules(word, expected):
    assert stem(word) == expected
    assert stem(word, aggressive=False) == word


def test_unknown_noun_forms_share_one_stem():
    assert stem("ጓደኞቻችን") == stem("ጓደኞች")


@pytest.mark.parametrize("word", ["አየሁ", "አነበቡ", "ይወዳል", "ናቸው", "ነው", "ውስጥ", "ከበደ", "hello", "።", "123"])
def test_words_that_must_not_change(word):
    assert stem(word) == word


def test_stemmer_class():
    stemmer = AmharicStemmer()
    assert stemmer.stem("ተማሪዎችን") == "ተማሪ"
    assert stemmer.stem_words(word_tokenize("ተማሪዎቹ መጻሕፍትን አነበቡ።")) == [
        "ተማሪ", "መጻሕፍት", "አነበቡ", "።",
    ]
    assert stem_words(["ተማሪዎች", "ላሞች"]) == ["ተማሪ", "ላም"]
    careful = AmharicStemmer(aggressive=False)
    assert careful.stem("አሠሪዎች") == "አሠሪዎች"


def test_stemmer_with_custom_tokenizer():
    tok = AmharicTokenizer(default_lexicon=False, lexicon=["ጋዜጣ"])
    assert AmharicStemmer(tok).stem("ጋዜጣን") == "ጋዜጣ"


def test_cli_stem():
    buf = io.StringIO()
    with redirect_stdout(buf):
        assert main(["--stem", "ተማሪዎችን መጻሕፍትን።"]) == 0
    assert buf.getvalue().strip() == "ተማሪ መጻሕፍት ።"
