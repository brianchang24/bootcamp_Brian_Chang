# Stakeholder Handoff Summary

## Overview & Purpose
We built a daily “up/down” signal using engineered price features. This package includes a saved model, a reproducible analysis, and an API to request predictions or re-run the full evaluation.

## Key Findings & Recommendations
- Baseline logistic model achieves ~60% accuracy on recent holdout with tuned threshold.
- Threshold tuning trades off precision vs recall; choose based on risk appetite.
- Use the `/run_full_analysis` endpoint to regenerate metrics and charts for any new processed file.

## Assumptions & Limitations
- Features and distributions are stable enough for out-of-sample use.
- Sentiment data is excluded (sparse timing).
- Model is a baseline; not production-hardened, no calibration.

## Risks
- Regime changes degrade performance.
- Data pipeline breaks if feature names change.
- Class imbalance may vary over time.

## How to Use Deliverables
- **API:** start with `python app.py`, check `/health`, then `POST /predict` or `/run_full_analysis`.
- **Reports:** see `reports/` for metrics CSV and charts.
- **Reproducibility:** run from fresh clone with `pip install -r requirements.txt`.

## Next Steps
- Extend features (nonlinear terms, interactions), add calibration, and monitor drift.
- Consider Streamlit dashboard for stakeholder demos.
