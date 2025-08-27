# Earnings Announcement Signal — Delivery Report (Stage 12)

**Repo path:** `/deliverables/final_report.md`  
**Audience:** Quant PMs, traders, and risk stakeholders  
**Date:** 8/27/2025

---

## Executive Summary

- **Best configuration:** Logistic regression with **tuned threshold ~0.44** delivered the highest **F1 = 0.735** and **Recall = 0.926**, with **Accuracy = 0.617**. It prioritizes catching up-moves while keeping precision acceptable.  
- **Limits:** **ROC AUC ≈ 0.535** across scenarios → probabilities are weakly separative; treat outputs as a **directional filter**, not a calibrated probability.  
- **Where it works best:** Accuracy is higher in **high-volatility regimes** (~0.75, wide CI given small n) vs **low-volatility** (~0.59). Use regime awareness in deployment.

---

## Key Charts

### 1) Scenario performance with uncertainty
![Scenario F1 with 95% bootstrap CI](/project/outputs/stage11_f1_ci.png)

**Takeaway:** Threshold tuning improves F1 and Recall (CI overlap indicates modest but consistent gains).

### 2) Confusion matrix (best scenario)
![Confusion matrix — tuned threshold](/project/outputs/stage11_confusion_best.png)

**Takeaway:** Tuned threshold boosts true positives (Up days caught), trading some precision.

### 3) Accuracy by volatility regime
![Accuracy by volatility regime with 95% CI](/project/outputs/stage11_subgroup_vol.png)

**Takeaway:** Model is **more reliable during HighVol**; in LowVol, edge is smaller and noisier.


---

## Sensitivity Summary (scenarios)

**Scenarios compared:**  
- `logit_base` (threshold 0.50)  
- `logit_balanced` (threshold 0.50, class_weight='balanced')  
- `logit_base_tunedthr` (threshold ≈ **0.44** to maximize F1 on train)

| Scenario              | Threshold | Accuracy | Precision | Recall | F1     | ROC AUC |
|-----------------------|-----------|----------|-----------|--------|--------|---------|
| logit_base_tunedthr   | **0.44**  | **0.617**| 0.610     | **0.926** | **0.735** | 0.535   |
| logit_base            | 0.50      | 0.596    | **0.633** | 0.704  | 0.667 | 0.535   |
| logit_balanced        | 0.50      | 0.574    | 0.640     | 0.593  | 0.615 | 0.535   |

**Interpretation:**  
- Tuning the **threshold** is the highest-impact scenario change for this problem.  
- **Class weighting** did not yield gains here.  
- ROC AUC is ~0.53 across cases → coarse discrimination; use **thresholded signals** and **regime filters**.

---

## Assumptions & Risks

- **Stationarity:** We assume today’s feature/label relationships resemble the backtest period. Regime shifts (macro shocks, structural changes) may break the edge.  
- **Heteroscedasticity / noise:** Daily returns are noisy; probabilities are not well calibrated. Prefer **classification thresholds** over raw probabilities.  
- **Threshold dependence:** Business objectives (precision vs. recall) should set the operating point. Re-tune thresholds over time.  
- **Data hygiene:** Outliers and missing values are handled per earlier stages; if missingness grows or becomes non-random, re-evaluate imputation and sensitivity.

---

## Decision Implications

- Use the signal as a **filter** (e.g., only act when P(Up) ≥ 0.44 **and** HighVol regime).  
- Expect **more benefit in volatile markets**; in quiet markets, reduce weight or combine with other signals.  
- Monitor weekly: accuracy/F1 with **bootstrap CIs**, plus drift checks on feature distributions and threshold stability.  
- Combine with additional features (e.g., regime indicators, cross-asset context) or ensemble models for robustness.

---

## Next Steps

1. **Operationalize thresholding:** auto-tune on rolling windows to keep F1 stable.  
2. **Regime features:** explicit regime detector (e.g., volatility state) to gate signal usage.  
3. **Model enrichment:** try gradient boosting / calibrated models with careful time splits.  
4. **Monitoring:** ship dashboards for weekly metrics + bootstrap CIs; alert on drift.

---

## Reproducibility & Artifacts

- **Notebook(s):**  
  - `notebooks/11_evaluation_risk.ipynb`    
- **Images:** `outputs/`  
  - `stage11_f1_ci.png`, `stage11_confusion_best.png`, `stage11_subgroup_vol.png`  
- **Tables:**  
  - `outputs/stage11_scenarios_summary.csv`
- **Data:** `data/processed/prices_with_tech_features_model.csv`

---
