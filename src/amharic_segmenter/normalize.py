"""Optional orthographic normalisation for Amharic text.

Amharic has several groups of letters that are pronounced identically
(ሀ/ሐ/ኀ, ሰ/ሠ, አ/ዐ, ጸ/ፀ).  Writers use them inconsistently, which fragments
vocabulary in NLP pipelines.  :func:`normalize_homophones` collapses each
group to one representative while preserving the vowel order, and it never
changes the length of the text (so token offsets stay valid).
"""
from __future__ import annotations

# source block start -> representative block start (7 vowel orders each)
_BLOCKS = {
    0x1210: 0x1200,  # ሐ -> ሀ
    0x1280: 0x1200,  # ኀ -> ሀ
    0x1220: 0x1230,  # ሠ -> ሰ
    0x12D0: 0x12A0,  # ዐ -> አ
    0x1340: 0x1338,  # ፀ -> ጸ
}

_TABLE = {
    src + i: dst + i
    for src, dst in _BLOCKS.items()
    for i in range(7)
}


def normalize_homophones(text: str) -> str:
    """Collapse homophone letter families to a single representative."""
    return text.translate(_TABLE)
