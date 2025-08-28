# Deployment & Monitoring Reflection

## Risks if deployed.
- **Data drift**: engineered features (e.g., gap\_pct, rsi\_14) shift under new volatility regimes.

- **Data quality**: late/missing bars, schema changes, or upstream symbol holidays create leakage or empty rows.

- **Label issues**: next-day returns can be delayed or revised (corporate actions).

- **Model brittleness**: linear boundary underperforms in sudden regime changes; threshold tuned on a narrow period.

- **System fragility**: batch job failures or silent partial loads cause stale predictions.

## What I’ll monitor
**Data:**
- Freshness: max time since last trading day ingest ≤ **24h**; alert if > 24h.
- Null/NA rate per feature ≤ **1%**; schema hash must match; PSI on key features < **0.2** (warn at 0.1).

**Model:**
- 10-day rolling **AUC** ≥ **0.60** (warn at 0.58); accuracy ≥ **0.55**; Brier score not > **20%** above baseline.
- Calibration drift (expected vs observed up-rate); threshold health (precision/recall trade-off weekly).

**System:**
- ETL success rate ≥ **99%**; p95 API latency ≤ **500ms**; error rate < **0.5%**; job runtime SLA ±20%.

**Business:**
- Hit-rate vs benchmark (e.g., delta vs sign-flip baseline) weekly; simple **PnL** backtest and turnover; coverage (predictions/trading days).

## Ownership & handoffs
- **Data ops (primary):** monitor freshness/schema; first step: pause downstream scoring, backfill missing day, re-run validation.
- **Model owner (me):** investigate metric drops; first step: compare current/last 30-day PSI and recalibrate threshold; retrain if PSI > **0.2** or 2-week AUC < **0.60**.
- **Platform/on-call:** respond to API/ETL incidents; rollback to last **model.pkl** if scoring fails.
- **Cadence:** weekly review; scheduled retrain **monthly** or on triggered drift; all incidents logged in repo issues with a brief RCA and next actions.
