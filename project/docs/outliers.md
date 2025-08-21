# Outlier Analysis

## Definition of Outliers
We define **outliers** as data points that deviate significantly from the majority of the distribution.  
For daily returns (`ret_1d`), we tested two approaches:

- **IQR Method**: Points outside `[Q1 – 1.5 × IQR, Q3 + 1.5 × IQR]`
- **Z-Score Method**: Points with standardized absolute value `|z| > 3`

Both methods assume different distributional properties:
- IQR is robust for skewed/non-normal data.
- Z-score is most appropriate under (approximate) normality.

---

## Methods Applied
- Implemented functions in `src/outliers.py`:
  - `detect_outliers_iqr(series, k=1.5)`
  - `detect_outliers_zscore(series, threshold=3.0)`
- Created boolean flags (`outlier_iqr`, `outlier_z`) in the notebook.
- Compared flagged counts and overlap.

---

## Flagging Results
- **Fraction flagged**:  
  - IQR: **8.4%**  
  - Z-score: **1.6%**

- **Overlap counts**:

| outlier_iqr | outlier_z False | outlier_z True |
|-------------|-----------------|----------------|
| False       | 229             | 0              |
| True        | 17              | 4              |

**Interpretation:**  
The IQR method flagged far more points (21 total) than the Z-score method (4 total).  
Only 4 points overlapped between the two methods.

---

## Sensitivity Analysis

### Summary Statistics of Returns
| Method            | Mean     | Median   | Std Dev  |
|-------------------|----------|----------|----------|
| All               | 0.031760 | 0.114025 | 2.024903 |
| Filtered (IQR)    | 0.092742 | 0.118700 | 1.214030 |
| Filtered (Z-score)| 0.011425 | 0.114025 | 1.572850 |

**Observations:**
- Removing IQR outliers **increased the mean** and lowered standard deviation, pulling the distribution tighter.  
- Removing Z-score outliers had a smaller effect, but still reduced variance.  
- Median remained stable across methods, showing central tendency is robust.  

---

## Assumptions
- IQR assumes quartiles summarize central tendency well.  
- Z-score assumes normality (may mislabel points in skewed/heavy-tailed data).  
- Outliers are assumed to be data “errors” or extreme shocks — not structural features.

---

## Risks
- Over-filtering may discard **true market events** (e.g., earnings shocks, crash days).  
- Under-filtering leaves inliers that distort volatility and risk estimates.  
- Choice of threshold (e.g., `3σ` for Z-score or `1.5×IQR`) is somewhat arbitrary and must be justified.

---

## Visuals
See `notebooks/stage07_outliers.ipynb` for:
- Boxplots before/after filtering  
- Histograms with overlay of winsorized vs. raw returns
