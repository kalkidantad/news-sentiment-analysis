#!/usr/bin/env python3
"""Read news CSV from ``data/raw`` (or ``EDA_NEWS_PATH``), write normalized CSV to ``data/newdata``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from news_io import load_normalized_news, project_root, resolve_news_csv, write_newdata_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV path (default: data/newdata/news_normalized.csv)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root (default: parent of scripts/)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else project_root()

    csv_in = resolve_news_csv(root)
    df = load_normalized_news(csv_in)
    out = args.output
    if out is None:
        out = root / "data" / "newdata" / "news_normalized.csv"
    else:
        out = out.expanduser().resolve()

    write_newdata_csv(df, out)
    print("Source:", csv_in)
    print("Rows:", len(df))
    print("Wrote:", out)


if __name__ == "__main__":
    main()
