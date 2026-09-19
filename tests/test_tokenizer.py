"""Tests for word- and sentence-level tokenization."""
import pytest

from amharic_segmenter import AmharicTokenizer, sentence_tokenize, tokenize, tokenize_spans


def test_basic_words_and_full_stop():
    assert tokenize("አበበ ከበደን አየ።") == ["አበበ", "ከበደን", "አየ", "።"]


def test_old_style_word_separator():
    # The grammar book separates words with ፡ and ends sentences with ፡፡ or ።
    assert tokenize("አበበ፡ከበደን፡አየ፡፡") == ["አበበ", "፡", "ከበደን", "፡", "አየ", "፡፡"]


def test_ethiopic_punctuation_marks_are_single_tokens():
    assert tokenize("አዎ፣ እሺ፤ እሺ፧") == ["አዎ", "፣", "እሺ", "፤", "እሺ", "፧"]


def test_numbers_latin_and_mixed_text():
    assert tokenize("ዋጋው 3.5 ብር ነው፤ ፩፻ hello-world") == [
        "ዋጋው", "3.5", "ብር", "ነው", "፤", "፩፻", "hello-world",
    ]


def test_exclude_punctuation():
    assert tokenize("እሺ፣ አዎ።", include_punct=False) == ["እሺ", "አዎ"]


@pytest.mark.parametrize(
    "text",
    [
        "አበበ ከበደን አየ።",
        "አበበ፡ከበደን፡አየ፡፡",
        "ሰላም! Hello, world 123 ... ok?",
        "emoji \U0001F600 and _underscore_ እና ፩፪፫",
        "",
        "   \n\t ",
    ],
)
def test_no_character_is_ever_lost(text):
    assert "".join(tokenize(text)) == "".join(text.split())


def test_spans_point_back_into_the_text():
    text = "ተማሪዎች በከተማ ይኖራሉ።"
    spans = tokenize_spans(text)
    assert [text[t.start:t.end] for t in spans] == [t.text for t in spans]
    assert [t.kind for t in spans] == ["word", "word", "word", "punct"]


def test_sentence_splitting():
    text = "አበበ መጣ። ከበደ ሄደ፧ እሺ! እሺ፡፡ ጨረሰ"
    assert sentence_tokenize(text) == ["አበበ መጣ።", "ከበደ ሄደ፧", "እሺ!", "እሺ፡፡", "ጨረሰ"]


def test_sentence_splitting_keeps_decimal_numbers_together():
    assert sentence_tokenize("ዋጋው 3.5 ነው። እሺ።") == ["ዋጋው 3.5 ነው።", "እሺ።"]


def test_sentence_splitting_empty_input():
    assert sentence_tokenize("") == []
    assert sentence_tokenize("  \n ") == []


def test_invalid_strategy_is_rejected():
    with pytest.raises(ValueError):
        AmharicTokenizer(strategy="magic")
