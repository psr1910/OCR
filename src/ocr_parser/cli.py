from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import OCRTextParser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse OCR text into structured JSON.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to a UTF-8 text file. Reads stdin when omitted.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to write the parsed JSON result.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = _read_text(args.input)
    parsed = OCRTextParser().parse(text).to_dict()
    indent = 2 if args.pretty else None
    output = json.dumps(parsed, ensure_ascii=False, indent=indent)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0


def _read_text(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
