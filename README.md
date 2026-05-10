# News Sentiment Analysis

Exploratory and predictive analysis linking **financial news headlines** (FNSPID-style) to **equity prices** for Nova Financial Solutions.

## Repository layout

| Path | Purpose |
|------|---------|
| `data/raw/` | Source headlines CSV (`financial_news.csv` or bundled `sample_news.csv`) |
| `data/newdata/` | Optional local folder for normalized or derived extracts (typically `*.csv`; see [.gitignore](.gitignore)) |
| `notebooks/` | Jupyter notebooks (EDA and later modeling) |
| `src/` | Shared Python modules (extend as pipelines grow) |
| `tests/` | Automated checks (`pytest`) |
| `scripts/` | CLI or batch helpers (see [scripts/README.md](scripts/README.md)) |

## Data

Your **input** CSV should match the usual FNSPID-style fields (matched case-insensitively):

- `headline` — article title  
- `url` — article link (required on disk for validation with the sample schema; **not kept** in the analysis dataframe—the notebook selects `headline`, `publisher`, `date`, and `stock` only)  
- `publisher` — author or outlet  
- `date` — publication datetime (timezone-aware preferred; UTC is used internally after parsing)  
- `stock` — ticker symbol (e.g. `AAPL`)

Exports whose first column is an automatic row index (`Unnamed: 0`, etc.) drop those `Unnamed*` columns before validation.

### Local setup

1. Put the full dataset at `data/raw/financial_news.csv`, or symlink it there. Prefer **not** to commit large dumps.  
2. `data/raw/sample_news.csv` is included so CI and lightweight clones always have usable input.

**Override CSV path**

Set **`EDA_NEWS_PATH`** (shell environment variable) to the CSV you want—for example export it in the terminal before launching Jupyter:

```bash
export EDA_NEWS_PATH=/path/to/your_dump.csv
jupyter notebook notebooks/01_eda_financial_news.ipynb
```

Resolution order: `EDA_NEWS_PATH`, then `data/raw/financial_news.csv`, then `data/raw/sample_news.csv`.

Normalized or intermediate tables you produce locally may go under **`data/newdata/`**; keep large `*.csv` files out of version control unless they are deliberate small artifacts.

**.gitignore** (high level): `data/raw/*.csv` except `sample_news.csv`; `data/newdata/*.csv`; `**/raw_analyst_ratings.csv`; ignored paths under `data/raw/newsData/`.

### Task 2 — prices, TA-Lib, PyNance

Notebook: `notebooks/02_technical_analysis_talib_pynance.ipynb` downloads **daily OHLCV** with [**yfinance**](https://pypi.org/project/yfinance/) (tickers inferred from `data/raw/sample_news.csv` plus `SPY`), or loads a local CSV if you set **`YFINANCE_OFFLINE_CSV`**. Indicators use [**TA-Lib**](https://pypi.org/project/TA-Lib/) (binary wheels cover many Linux/macOS/Windows setups; source builds still need the underlying TA-Lib C library). Supplementary metrics use [**PyNance**](https://pypi.org/project/pynance/).

## Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run notebooks:

```bash
jupyter notebook notebooks/01_eda_financial_news.ipynb
jupyter notebook notebooks/02_technical_analysis_talib_pynance.ipynb
```

Use the **same interpreter** where you ran `pip install`: in Cursor / VS Code, choose the **`./.venv/bin/python`** kernel (Windows: `.venv\Scripts\python.exe`). Missing `sklearn`, `talib`, or `yfinance` in-cell almost always means the wrong kernel—switch interpreter or reinstall requirements in that env. Optional kernel registration:

```bash
python -m ipykernel install --user --name news-sentiment --display-name "Python (news-sentiment .venv)"
```

## Branches

- `main` — integration  
- `task-1` — EDA deliverables per challenge brief  
- `task-2` — technical indicators (`TA-Lib`, `PyNance`) and interim reporting  

## CI

GitHub Actions runs `pytest tests/` on push and pull requests.
