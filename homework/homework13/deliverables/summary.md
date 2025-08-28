# Stakeholder Summary – Model Deployment Homework

## Key Metrics
- **Accuracy:** ~60% (best logistic regression variant with tuned threshold)
- **Precision:** ~0.61 (probability that predicted “up” is truly “up”)
- **Recall:** ~0.93 (most actual “up” days are caught, though with trade-off in false positives)
- **RMSE (regression variant):** ~1.43

## High-Level Assumptions
- Daily returns are approximately stationary and can be modeled with lag/rolling features.
- Logistic regression provides a linear decision boundary in feature space.
- Train/test split preserves time ordering (no leakage).

## Risks & Limitations
- **Volatility Regimes:** Model accuracy varies between low- and high-volatility periods.
- **Data Coverage:** Sentiment data was sparse and excluded from final features.
- **Linear Assumption:** Relationships may be nonlinear; tree-based models showed worse holdout performance, but more tuning may be needed.
- **Sample Size:** Limited observations mean results are sensitive to scenario choices.

## Sensitivity Analysis
- **Threshold Adjustment:** Lowering the decision threshold (0.44 vs 0.50) improved recall significantly but reduced precision.
- **Imputation / Outlier Rules:** Different treatments shift coefficients and error bars but don’t change overall conclusions.

## What This Means
- The model is **better at catching “up” signals than avoiding false alarms** — suitable if the stakeholder values not missing opportunities more than avoiding mistakes.
- Before production use, further validation across different volatility regimes is required.
- Next step: test richer features (e.g., nonlinear transformations, interaction terms, sentiment) and evaluate stability across more periods.

---
