# Earnings Announcement Sentiment Impact

**Stage:** Problem Framing & Scoping (Stage 01)  

## Problem Statement
Public companies publish quarterly earnings announcements that can move prices quickly. Traders and analysts need a fast way to judge whether the tone of an announcement suggests a likely **up** or **down** move on the next trading day. Without a quick signal, they may miss opportunities or take on avoidable risk.

## Stakeholder & User
- **Primary stakeholder:** Quantitative traders on the buy side.
- **End users:** Buy-side equity analysts and trading assistants who act on an alert.
- **Workflow context:** Intraday and T+1 decisions around scheduled earnings release windows.

## Useful Answer & Decision
- **Type:** Predictive classification (positive vs. negative next-day return), with a probability score.
- **Primary metric(s):** Accuracy / F1 on sign prediction; AUC; uplift vs. baseline; PnL in a simple backtest.
- **Artifact(s):** CSV/JSON of signals + a simple notebook/CLI that outputs scores for a given ticker/date.

## Assumptions & Constraints
- Earnings text (press releases, prepared remarks) and historical prices are available for chosen tickers.
- Release timestamps can be aligned to market sessions (AMC/BMO).
- Low-latency isn’t required for MVP; near-real-time would be “nice to have” later.
- Data access and licensing will be respected.

## Known Unknowns / Risks
- Market moves may reflect macro news, guidance on calls, or surprises not captured in the text.
- Smaller firms may have limited or messy text disclosures.
- Leakage risk (using post-event info by mistake) must be controlled in labeling.

## Data Storage

**Folders**
- `data/raw/` — timestamped raw snapshots (CSV) saved during ingestion.
- `data/processed/` — typed/validated tables (Parquet) used by later stages.
**Formats**
- **CSV**: portable, human-readable.
- **Parquet**: efficient columnar format with better types and faster IO. Requires `pyarrow` or `fastparquet`.
**Configuration**
- Paths are read from `.env` (`DATA_DIR_RAW`, `DATA_DIR_PROCESSED`) using `python-dotenv`.
- Code never hardcodes absolute paths; it resolves relative to the project root.
**Utilities**
- `src/utils_storage.py` exposes `write_df` / `read_df` which route by file suffix and create missing directories.
- CSV reload auto-parses a `date` column if present.

## Lifecycle Mapping (Goal → Stage → Deliverable)
- Frame decision + users → Problem Framing & Scoping → This README + stakeholder memo.
- Set up tools/env → Tooling Setup → Repo tree `/data/ /src/ /notebooks/ /docs/` and config.
- Ingest data → Data Acquisition/Ingestion → Earnings text + next-day return labels dataset.
- Store safely → Data Storage → Versioned data files and schema notes in `/data/`.
- Clean & align → Data Preprocessing → Text cleaning, de-duplication, timestamp alignment.
- Check extremes → Outlier Analysis → Price jumps, missing/zero volumes, odd text lengths.
- Understand data → Exploratory Data Analysis → Label balance, sector splits, text stats.
- Build features → Feature Engineering → Sentiment scores (lexicon/model), basic text features.
- Train model → Modeling → Classifier with dated split; baseline vs. improved model.
- Validate → Evaluation & Risk Communication → Metrics + simple backtest and caveats.
- Share results → Results Reporting & Stakeholder Communication → Short brief + charts.
- Make it usable → Productization → Script/notebook that outputs signals from new text.
- Operate it → Deployment & Monitoring → Simple job + drift/quality checks (stretch).
- Scale/design → Orchestration & System Design → Future plan (optional).

## Repo Plan
project/
data/ # raw/processed data (with .gitkeep to track folder)
src/ # ingestion, preprocessing, features, modeling
notebooks/ # EDA, modeling experiments
docs/ # stakeholder memo / slide / diagrams
