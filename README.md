# News Sentiment Analysis

Exploratory and predictive analysis linking **financial news headlines** (FNSPID-style) to **equity prices** for Nova Financial Solutions.

## Repository layout

| Path | Purpose |
|------|---------|
| `data/raw/` | Place the full Financial News dataset CSV here |
| `notebooks/` | Jupyter notebooks (EDA and later modeling) |
| `src/` | Reusable Python modules |
| `tests/` | Automated tests (`pytest`) |
| `scripts/` | One-off CLI utilities |

## Data

Expected columns align with the FNSPID specification:

- `headline` — article title  
- `url` — article link  
- `publisher` — author or outlet  
- `date` — publication datetime (prefer timezone-aware; spec references UTC−4)  
- `stock` — ticker symbol (e.g. `AAPL`)

**Local setup**

1. Copy your full dataset to `data/raw/financial_news.csv` (or symlink your export; set `EDA_NEWS_PATH` in the notebook to point at any path). Exports whose first CSV column is a row index (for example Benzinga `raw_analyst_ratings`-style dumps) drop `Unnamed` columns automatically.  
2. A small `data/raw/sample_news.csv` is bundled so EDA runs in CI and fresh clones without the full dump.

Do not commit massive CSVs—`.gitignore` excludes common raw paths (`data/raw/*.csv` except `sample_news.csv`; `**/raw_analyst_ratings.csv`).

Historical OHLCV data will be wired in later tasks (e.g. YFinance).

## Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the exploratory notebook:

```bash
jupyter notebook notebooks/01_eda_financial_news.ipynb
```

**Important:** Jupyter must use the **same Python** where you ran `pip install -r requirements.txt`. In Cursor / VS Code, use the notebook **kernel / interpreter picker** and select `.venv/bin/python` from this repo. If `sklearn` is missing in the notebook, you are almost certainly on the wrong interpreter. Optional: register that env once with `python -m ipykernel install --user --name news-sentiment --display-name "Python (news-sentiment .venv)"`.

## Branches

- `main` — integration  
- `task-1` — EDA deliverables per challenge brief  

## CI

GitHub Actions runs `pytest tests/` on push and pull request.
