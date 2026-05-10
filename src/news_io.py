"""Load FNSPID-style news CSVs from ``data/raw`` and normalize columns."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

EXPECTED = frozenset({"headline", "url", "publisher", "date", "stock"})


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_news_csv(
    root: Path | None = None,
    *,
    env_var: str = "EDA_NEWS_PATH",
) -> Path:
    root = root or project_root()
    raw = root / "data" / "raw"
    primary = raw / "financial_news.csv"
    fallback = raw / "sample_news.csv"

    env = os.environ.get(env_var)
    if env:
        p = Path(env).expanduser()
        if not p.is_file():
            raise FileNotFoundError(env)
        return p
    if primary.is_file():
        return primary
    if fallback.is_file():
        return fallback
    raise FileNotFoundError(
        "No news CSV found. Place FNSPID export at data/raw/financial_news.csv "
        "or data/raw/sample_news.csv, or set EDA_NEWS_PATH."
    )


def load_normalized_news(csv_path: Path) -> pd.DataFrame:
    df_raw = pd.read_csv(csv_path)
    unnamed = [c for c in df_raw.columns if str(c).startswith("Unnamed")]
    df_raw = df_raw.drop(columns=unnamed)

    cols_lower = {str(c).lower() for c in df_raw.columns}
    missing = EXPECTED - cols_lower
    if missing:
        raise ValueError(f"CSV missing columns (case-insensitive): {sorted(missing)}")

    cols = {c.lower(): c for c in df_raw.columns}
    col_h, col_p, col_d, col_s = cols["headline"], cols["publisher"], cols["date"], cols["stock"]

    df = df_raw[[col_h, col_p, col_d, col_s]].rename(
        columns={col_h: "headline", col_p: "publisher", col_d: "date", col_s: "stock"}
    ).copy()

    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df["headline_len"] = df["headline"].astype(str).str.len()
    df["word_count"] = df["headline"].astype(str).str.split().map(len)
    return df


def write_newdata_csv(df: pd.DataFrame, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path
