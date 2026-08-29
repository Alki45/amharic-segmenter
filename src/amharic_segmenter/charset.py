"""Low-level helpers for the Ethiopic (Fidel) script.

Each Ethiopic consonant occupies a block of 8 consecutive code points, one per
vowel *order*.  The first seven are the classic orders used in Amharic
grammar books (the names below follow the traditional Ge'ez terminology):

    0 ግዕዝ  (ä)   1 ካዕብ (u)   2 ሣልስ (i)   3 ራብዕ (a)
    4 ሃምስ  (e)   5 ሳድስ (ə / no vowel)   6 ሳብዕ (o)

The eighth slot of a block is a labialised form (e.g. ሏ) and is ignored here.
A few blocks (e.g. ቈ, ኰ, ጐ) are irregular in Unicode and are deliberately
left out, because they never occur as word-final letters in ordinary text.
"""
from __future__ import annotations

GEEZ, KAEB, SALIS, RABI, HAMIS, SADIS, SABI = range(7)

ORDER_NAMES = ("ግዕዝ", "ካዕብ", "ሣልስ", "ራብዕ", "ሃምስ", "ሳድስ", "ሳብዕ")

_FIRST = 0x1200
_LAST_REGULAR = 0x1357
_IRREGULAR = (
    (0x1248, 0x124F),
    (0x1258, 0x125F),
    (0x1288, 0x128F),
    (0x12B0, 0x12B7),
    (0x12C0, 0x12C7),
    (0x1310, 0x1317),
)


def is_ethiopic_letter(ch: str) -> bool:
    """True for a character in the Ethiopic syllable range."""
    return _FIRST <= ord(ch) <= 0x135A


def _is_regular(cp: int) -> bool:
    if not (_FIRST <= cp <= _LAST_REGULAR):
        return False
    return not any(lo <= cp <= hi for lo, hi in _IRREGULAR)


def fidel_order(ch: str) -> int | None:
    """Return the vowel order (0-6) of a fidel, or ``None`` if not applicable."""
    cp = ord(ch)
    if not _is_regular(cp):
        return None
    order = (cp - _FIRST) % 8
    return order if order <= SABI else None


def is_wa_form(ch: str) -> bool:
    """True for the labialised 8th form of a letter (ሟ, ሏ, ጓ …).

    It is how the feminine ``ዋ`` is written when it fuses into a consonant,
    e.g. ሐኪም + ዋ -> ሐኪሟ.
    """
    cp = ord(ch)
    return _is_regular(cp) and (cp - _FIRST) % 8 == 7


def with_order(ch: str, order: int) -> str:
    """Return the fidel with the same consonant as ``ch`` in another vowel order."""
    current = fidel_order(ch)
    if current is None:
        raise ValueError(f"{ch!r} is not a regular Ethiopic syllable")
    if not 0 <= order <= SABI:
        raise ValueError("order must be between 0 and 6")
    return chr(ord(ch) - current + order)
