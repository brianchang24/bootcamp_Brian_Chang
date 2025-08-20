## Data Cleaning Strategy (Stage 06)

- **Missing values:** Filled numeric columns with the column median (robust to outliers).
- **Row/column removal:** Dropped rows with >60% missing (configurable threshold).
- **Scaling:** Z-score normalization on numeric columns; constant columns become 0.0.
- **Modularity:** Implemented in `src/cleaning.py` and imported in the notebook.
- **Outputs:** Saved cleaned dataset to `data/processed/sample_data_cleaned.csv`.
