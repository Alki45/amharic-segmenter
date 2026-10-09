"""Morphology tests.  Every example below is taken from the grammar book
አማርኛ ሠዋሰው (1963 E.C.) unless a comment says otherwise."""
import pytest

from amharic_segmenter import AmharicTokenizer, analyze, split_morphemes, tokenize
from amharic_segmenter.charset import RABI, SABI, SADIS, fidel_order, with_order


# -- object marker ን (book pp. 19-23, examples 35-40) -----------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("ከበደን", ["ከበደ", "ን"]),
        ("ይህን", ["ይህ", "ን"]),
        ("እሱን", ["እሱ", "ን"]),
    ],
)
def test_object_marker(word, expected):
    assert split_morphemes(word) == expected


# -- plural (book pp. 39-44) ---------------------------------------------------
@pytest.mark.parametrize(
    "singular, plural",
    [
        ("ፈረስ", "ፈረሶች"),
        ("ሰው", "ሰዎች"),
        ("ወረቀት", "ወረቀቶች"),
        ("ብዕር", "ብዕሮች"),
        ("መጽሐፍ", "መጽሐፎች"),
        ("በር", "በሮች"),
        ("ላም", "ላሞች"),
        ("በቅሎ", "በቅሎች"),
        ("ክፉ", "ክፉዎች"),
        ("ገበሬ", "ገበሬዎች"),
        ("ተማሪ", "ተማሪዎች"),
    ],
)
def test_plural_returns_the_singular_stem(singular, plural):
    a = analyze(plural)
    assert a.stem == singular
    assert a.suffixes in (("ች",), ("ዎች",))


def test_singular_words_are_left_alone():
    for word in ["ሰው", "ተማሪ", "ወንድም", "ላም", "ከበደ", "ቤት"]:
        assert split_morphemes(word) == [word]


# -- possessive suffixes and linking vowel (book pp. 25-27) -------------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("ቤትህን", ["ቤት", "ህ", "ን"]),
        ("ልብስሽን", ["ልብስ", "ሽ", "ን"]),
        ("አገራችሁን", ["አገር", "ችሁ", "ን"]),
        ("ችግራቸውን", ["ችግር", "ቸው", "ን"]),
        ("ተማሪዎቻችን", ["ተማሪ", "ዎች", "ችን"]),
    ],
)
def test_possessive_suffixes(word, expected):
    assert split_morphemes(word) == expected


# -- definite article ኡ / ው fused into the stem (book p. 24) --------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("ልጁን", ["ልጅ", "ው", "ን"]),
        ("ተማሪዎቹ", ["ተማሪ", "ዎች", "ው"]),
        ("ተማሪው", ["ተማሪ", "ው"]),
    ],
)
def test_definite_article(word, expected):
    assert split_morphemes(word) == expected


# -- conjunctions ና and ም (book pp. 57-60) ---------------------------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("ከበደና", ["ከበደ", "ና"]),
        ("ክፉና", ["ክፉ", "ና"]),
        ("ተማሪም", ["ተማሪ", "ም"]),
        ("ተማሪውንም", ["ተማሪ", "ው", "ን", "ም"]),
    ],
)
def test_conjunctions(word, expected):
    assert split_morphemes(word) == expected


# -- prepositions (book pp. 29-34) -------------------------------------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("በከተማ", ["በ", "ከተማ"]),
        ("ለተማሪ", ["ለ", "ተማሪ"]),
        ("ከቤት", ["ከ", "ቤት"]),
        ("ለተማሪዎቻችን", ["ለ", "ተማሪ", "ዎች", "ችን"]),
    ],
)
def test_prefixed_prepositions(word, expected):
    assert split_morphemes(word) == expected


def test_names_that_look_prefixed_are_not_split():
    # ከበደ starts with ከ and ለ/በ-words are only split if the rest is known.
    assert split_morphemes("ከበደ") == ["ከበደ"]
    assert split_morphemes("በደ") == ["በደ"]


# -- API behaviour -----------------------------------------------------------------------
def test_morphemes_option_in_tokenize():
    assert tokenize("ለተማሪዎች መጻሕፍት።", morphemes=True) == ["ለ", "ተማሪ", "ዎች", "መጻሕፍት", "።"]


def test_mark_affixes():
    assert tokenize("ተማሪውን", morphemes=True, mark_affixes=True) == ["ተማሪ", "+ው", "+ን"]
    assert tokenize("በከተማ", morphemes=True, mark_affixes=True) == ["በ+", "ከተማ"]


def test_unknown_stems_are_not_split_by_default_but_are_with_rules_strategy():
    assert split_morphemes("ጓደኞቻቸውን") == ["ጓደኞቻቸውን"]
    rules = AmharicTokenizer(strategy="rules")
    assert rules.split_morphemes("ጓደኞቻቸውን")[-2:] == ["ቸው", "ን"]


def test_strategy_none_never_splits():
    tok = AmharicTokenizer(strategy="none")
    assert tok.split_morphemes("ተማሪዎችን") == ["ተማሪዎችን"]


def test_custom_lexicon_and_add_words():
    tok = AmharicTokenizer(default_lexicon=False, lexicon=["መምህር"])
    assert tok.split_morphemes("መምህራንን") == ["መምህራንን"]
    assert tok.split_morphemes("መምህርን") == ["መምህር", "ን"]
    tok.add_words(["ጓደኛ"])
    assert tok.split_morphemes("ጓደኛን") == ["ጓደኛ", "ን"]


def test_non_ethiopic_words_pass_through():
    assert split_morphemes("hello") == ["hello"]
    assert tokenize("hello ተማሪዎች", morphemes=True) == ["hello", "ተማሪ", "ዎች"]


# -- fidel helpers --------------------------------------------------------------------------
def test_fidel_orders():
    assert fidel_order("ሰ") == 0
    assert fidel_order("ው") == SADIS
    assert fidel_order("ዎ") == SABI
    assert fidel_order("ዛ") == RABI
    assert fidel_order("a") is None
    assert with_order("ጅ", SABI) == "ጆ"
    assert with_order("ሶ", SADIS) == "ስ"


# -- pronoun contractions (book p. 30: በኔ, በሱ, እንዳንተ, ከኛ) ------------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("በኔ", ["በ", "እኔ"]),
        ("በሱ", ["በ", "እሱ"]),
        ("ከኛ", ["ከ", "እኛ"]),
        ("ለነሱ", ["ለ", "እነሱ"]),
        ("እንዳንተ", ["እንደ", "አንተ"]),
        ("እንደኔ", ["እንደ", "እኔ"]),
        ("ከኔን", ["ከ", "እኔ", "ን"]),
    ],
)
def test_pronoun_contractions(word, expected):
    assert split_morphemes(word) == expected


# -- feminine ዋ, also fused into the last letter (book pp. 51-53) -----------------------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("ድንጋይዋ", ["ድንጋይ", "ዋ"]),
        ("ሐኪሟ", ["ሐኪም", "ዋ"]),
        ("ተማሪዋ", ["ተማሪ", "ዋ"]),
    ],
)
def test_feminine_suffix(word, expected):
    assert split_morphemes(word) == expected


# -- irregular plurals and reduplicated adjective plurals (book pp. 42-44, 47-48) ---------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("መጻሕፍትን", ["መጻሕፍት", "ን"]),
        ("ቃላቶች", ["ቃላት", "ች"]),  # double plural, book p. 44
        ("ንጉሥን", ["ንጉሥ", "ን"]),
        ("ትልልቅ", ["ትልልቅ"]),
        ("ነገሥታት", ["ነገሥታት"]),
    ],
)
def test_irregular_plurals(word, expected):
    assert split_morphemes(word) == expected


def test_lemma():
    from amharic_segmenter import lemma

    assert lemma("መጻሕፍትን") == "መጽሐፍ"
    assert lemma("ተማሪዎችን") == "ተማሪ"
    assert lemma("ትልልቅ") == "ትልቅ"
    assert lemma("ቤትህ") == "ቤት"


# -- examples from chapter 4 (book pp. 61-62): suffix order plural -> ው -> ን -> ና -------
@pytest.mark.parametrize(
    "word, expected",
    [
        ("ጓዳውንና", ["ጓዳ", "ው", "ን", "ና"]),
        ("ጣራውን", ["ጣራ", "ው", "ን"]),
        ("ቤቱን", ["ቤት", "ው", "ን"]),
        ("ባለቤቶቹን", ["ባለቤት", "ች", "ው", "ን"]),
        ("ሴትዮዋ", ["ሴትዮ", "ዋ"]),
        ("ሴቶች", ["ሴት", "ች"]),
    ],
)
def test_chapter_four_examples(word, expected):
    assert split_morphemes(word) == expected
