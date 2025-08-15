## Background
Earnings press releases and prepared remarks often move prices, but reading and interpreting them fast is hard during busy windows.

## Objective
Provide a quick classification (Up/Down next day) with a probability score for scheduled earnings, so traders can prioritize names and size positions.

## Users & Decisions
- **Users:** Quant traders and equity analysts.
- **Decisions:** Focus list for open/close; position tilt (long/short/flat); urgency of manual review.

## Scope (MVP)
- Coverage: A small, liquid ticker set (e.g., 20–50 names).
- Input: Historical earnings text + price data.
- Output: CSV/JSON of {ticker, report_time, score, class}, plus a simple notebook/CLI.

## Data Plan (MVP)
- Price data: Daily OHLCV; compute next-day return relative to release timing (AMC/BMO).
- Text: Press releases / summaries; basic sentiment via lexicon or a light model.

## Assumptions
- Text sentiment correlates with short-horizon moves.
- Timestamp alignment is accurate.

## Risks / Mitigations
- **Macro confounds:** Log notable macro events; consider filtering high-vol days.
- **Leakage:** Split by date strictly; avoid using post-event info.
- **Overfitting:** Keep features simple; hold out recent quarters.

## Success Criteria
- Classification improvements vs. 50% baseline (Accuracy/F1/AUC).
- Positive backtest PnL after costs in a simple ruleset (stretch).

## Next Steps
1) Build ingestion + labels (T+1 direction).  
2) Clean text and align timestamps.  
3) Generate sentiment features and train a baseline classifier.  
4) Report metrics + risks to desk; iterate.
