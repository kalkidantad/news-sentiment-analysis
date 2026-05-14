# Scripts

Use this folder for **CLI helpers** (downloads, batch ETL, feature builds)—run them from the repository root (`python scripts/<name>.py`) so imports and paths resolve.

- **`raw_to_newdata.py`** — read an FNSPID-style CSV from `data/raw` (same resolution rules as notebook 01), write normalized columns under `data/newdata/` (`news_normalized.csv` by default).

Add new scripts beside notebooks/modules as pipelines grow.

- **`export_interim_report_figures.py`** — writes `reports/figures/*.png` (EDA + TA-Lib charts) for embedding in `reports/INTERIM_REPORT_WEEK1_TASK2.md`; requires network for yfinance unless you adapt the script to use `YFINANCE_OFFLINE_CSV`.

- **`task3_sentiment_return_correlation.py`** — Task 3 pipeline: NLTK VADER scores on headlines, maps each article’s **America/New_York calendar date** to the **next NYSE session** when needed (weekends/holidays), averages compound sentiment by `(stock, session)`, joins **same-day** close-to-close return \((C_t-C_{t-1})/C_{t-1}\times100\) from yfinance, prints **Pearson r**, writes `reports/figures/task3_scatter_sentiment_vs_return.png`, `task3_bar_return_by_sentiment_category.png`, and `data/newdata/task3_stock_day_panel.csv` (gitignored like other `newdata/*.csv`). First run downloads the VADER lexicon via NLTK (network).
