# Stage 9 Pivot Memo — Sentiment Coverage & Project Direction

## What we tried
- Integrated real news sentiment via Alpha Vantage (article-level → daily NY date; then aligned to trading days).
- Result: only ~40–60 sentiment days over the year, heavily clustered near month-end.

## What we observed
- Many calendar days had **no articles**; weekend articles often dropped when aligning to trading days.
- Coverage bias: sentiment concentrated toward month-end (likely API sampling/limits), which distorts daily analysis.

## Decision
- **Keep the sentiment dataset** in `data/raw/` and `data/processed/` for transparency and future work.
- **Pivot core project goal to daily technical features** derived from OHLCV (always available, robust for modeling).
- Sentiment becomes **auxiliary** (documented limitation; can be revisited with a richer provider).

## New Goal (updated)
Predict or analyze **next-day return** using **daily technical features** (volatility, gaps, moving averages, RSI, volume shocks), with clear evaluation and risk notes. Sentiment will be optional context, not a primary signal.

## Implications
- Daily granularity preserved (≈250 rows).
- Features reproducible from prices; no external API dependency.
- Future extension: replace current sentiment source or add earnings-call text with a domain model (FinBERT).
