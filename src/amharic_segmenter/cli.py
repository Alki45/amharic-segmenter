"""Command line interface: ``amharic-segmenter`` / ``python -m amharic_segmenter``."""
from __future__ import annotations

import argparse
import json
import sys

from ._version import __version__
from .tokenizer import AmharicTokenizer


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="amharic-segmenter",
        description="Tokenize Amharic text into sentences, words or morphemes.",
    )
    p.add_argument("text", nargs="?", help="text to tokenize (reads stdin when omitted)")
    p.add_argument("-s", "--sentences", action="store_true", help="split into sentences instead of words")
    p.add_argument(
        "-m", "--morphemes", action="store_true", help="split words into prefixes, stems and suffixes"
    )
    p.add_argument("--stem", action="store_true", help="print the stem of every word")
    p.add_argument("--mark-affixes", action="store_true", help="write prefixes as 'በ+' and suffixes as '+ን'")
    p.add_argument("--strategy", choices=["lexicon", "rules", "none"], default="lexicon",
                   help="morpheme splitting strategy (default: lexicon)")
    p.add_argument("--lexicon", metavar="FILE", help="UTF-8 file with extra stems, one per line")
    p.add_argument(
        "--normalize", action="store_true", help="collapse homophone letters (ሐ->ሀ, ሠ->ሰ, ዐ->አ, ፀ->ጸ)"
    )
    p.add_argument("--no-punct", action="store_true", help="drop punctuation tokens")
    p.add_argument("--json", action="store_true", help="print the result as JSON")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for stream in (sys.stdout, sys.stdin):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

    text = args.text if args.text is not None else sys.stdin.read()
    kwargs = dict(strategy=args.strategy, normalize=args.normalize)
    tok = (AmharicTokenizer.from_file(args.lexicon, **kwargs) if args.lexicon
           else AmharicTokenizer(**kwargs))

    if args.stem:
        result = [tok.stem(t.text) for t in tok.tokenize_spans(text, include_punct=not args.no_punct)
                  if t.kind != "punct" or not args.no_punct]
        sep = " "
    elif args.sentences:
        result = tok.sentence_tokenize(text)
        sep = "\n"
    else:
        result = tok.tokenize(
            text,
            morphemes=args.morphemes,
            include_punct=not args.no_punct,
            mark_affixes=args.mark_affixes,
        )
        sep = " "

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(sep.join(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
