import io
import json
from contextlib import redirect_stdout

import pytest

from amharic_segmenter import AmharicTokenizer, normalize_homophones
from amharic_segmenter.cli import main


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("ሐኪም", "ሀኪም"),
        ("ሠራተኛ", "ሰራተኛ"),
        ("ፀሐይ", "ጸሀይ"),
        ("ዐለም", "አለም"),
    ],
)
def test_homophone_normalisation(raw, expected):
    assert normalize_homophones(raw) == expected


def test_normalisation_preserves_length_and_other_text():
    text = "ሠራተኛ ሐኪም hello 123 ።"
    assert len(normalize_homophones(text)) == len(text)
    assert normalize_homophones("hello 123 ።") == "hello 123 ።"


def test_tokenizer_normalize_option_matches_lexicon():
    # The lexicon contains ሠራተኛ; with normalize=True spelling variants still match.
    tok = AmharicTokenizer(normalize=True)
    assert tok.split_morphemes("ሠራተኞች") == ["ሰራተኛ", "ች"]
    assert tok.split_morphemes("ሰራተኞች") == ["ሰራተኛ", "ች"]
    assert tok.split_morphemes("ሐኪሞች") == ["ሀኪም", "ች"]


def _run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue().rstrip("\n")


def test_cli_words():
    assert _run(["አበበ ከበደን አየ።"]) == (0, "አበበ ከበደን አየ ።")


def test_cli_morphemes_marked():
    assert _run(["-m", "--mark-affixes", "ተማሪዎችን"]) == (0, "ተማሪ +ዎች +ን")


def test_cli_sentences_json():
    code, out = _run(["--sentences", "--json", "አበበ መጣ። ከበደ ሄደ።"])
    assert code == 0
    assert json.loads(out) == ["አበበ መጣ።", "ከበደ ሄደ።"]
