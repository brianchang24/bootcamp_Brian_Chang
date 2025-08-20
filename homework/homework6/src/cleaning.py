# homework/homework6/src/cleaning.py
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Iterable, Optional

def _ensure_columns(df: pd.DataFrame, columns: Optional[Iterable[str]]) -> list[str]:
    """If columns is None, default to numeric columns; else validate they exist."""
    if columns is None:
        cols = df.select_dtypes(include=["number"]).columns.tolist()
    else:
        cols = list(columns)
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(f"Columns not in DataFrame: {missing}")
    return cols

def fill_missing_median(df: pd.DataFrame, columns: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """
    Fill NaNs in specified (or numeric) columns with the column median.
    Returns a NEW DataFrame (original is not mutated).
    """
    out = df.copy()
    cols = _ensure_columns(out, columns)
    for c in cols:
        med = out[c].median(skipna=True)
        out[c] = out[c].fillna(med)
    return out

def drop_missing(
    df: pd.DataFrame,
    threshold: float = 0.5,
    axis: str = "rows",
) -> pd.DataFrame:
    """
    Drop rows or columns whose fraction of missing values exceeds `threshold`.
    axis='rows'  -> drop rows with (na_count / n_cols) > threshold
    axis='cols'  -> drop columns with (na_count / n_rows) > threshold
    """
    if not 0 <= threshold <= 1:
        raise ValueError("`threshold` must be between 0 and 1.")
    out = df.copy()
    if axis.lower() in ("rows", "row", "r"):
        frac = out.isna().mean(axis=1)
        out = out.loc[frac <= threshold].copy()
    elif axis.lower() in ("cols", "columns", "c", "column"):
        frac = out.isna().mean(axis=0)
        keep_cols = [c for c, f in frac.items() if f <= threshold]
        out = out[keep_cols].copy()
    else:
        raise ValueError("`axis` must be 'rows' or 'cols'.")
    return out

def normalize_data(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
    method: str = "zscore",
) -> pd.DataFrame:
    """
    Normalize/scale numeric columns.
    method='zscore' -> (x - mean) / std (if std==0, result becomes 0 for that column)
    """
    out = df.copy()
    cols = _ensure_columns(out, columns)
    method = method.lower()
    if method not in ("zscore",):
        raise ValueError("Only method='zscore' is implemented in this homework.")

    for c in cols:
        series = out[c].astype(float)
        mu = series.mean()
        sd = series.std(ddof=0)
        if sd == 0 or np.isclose(sd, 0.0):
            out[c] = 0.0  # constant column -> all zeros after normalization
        else:
            out[c] = (series - mu) / sd
    return out
