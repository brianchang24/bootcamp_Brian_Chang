# project/src/cleaning.py
from __future__ import annotations
from typing import Iterable, Optional, Union
import numpy as np
import pandas as pd

# Generic

def _ensure_columns(df: pd.DataFrame, columns: Optional[Iterable[str]]) -> list[str]:
    """
    If columns is None -> default to numeric columns.
    Else -> validate they exist in df.
    """
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
    Returns a NEW DataFrame.
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
    axis='rows' -> drop rows with (na_count / n_cols) > threshold
    axis='cols' -> drop columns with (na_count / n_rows) > threshold
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
    Normalize numeric columns.
    method='zscore' -> (x - mean) / std (constant columns -> 0.0).
    """
    out = df.copy()
    cols = _ensure_columns(out, columns)
    method = method.lower()
    if method != "zscore":
        raise ValueError("Only method='zscore' supported.")
    for c in cols:
        s = out[c].astype(float)
        mu = s.mean()
        sd = s.std(ddof=0)
        out[c] = 0.0 if (sd == 0 or np.isclose(sd, 0.0)) else (s - mu) / sd
    return out

# Finance

def sort_and_cast_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure typical OHLCV schema and dtypes for downstream consistency.
    Expects columns: 'date','open','high','low','close','volume' (extra cols kept).
    """
    out = df.copy()
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
        out = out.sort_values("date")
    for c in ["open","high","low","close"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    if "volume" in out.columns:
        out["volume"] = pd.to_numeric(out["volume"], errors="coerce").astype("Int64")
    return out

def ffill_ohlcv_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Forward-fill small gaps for OHLCV columns after sorting by date.
    Use carefully: good for occasional missing values; not for large gaps.
    """
    out = sort_and_cast_ohlcv(df)
    cols = [c for c in ["open","high","low","close","volume"] if c in out.columns]
    out[cols] = out[cols].ffill()
    return out

def add_returns(df: pd.DataFrame, price_col: str = "close", out_col: str = "ret_1d") -> pd.DataFrame:
    """
    Compute simple daily return from the given price column.
    Assumes the DataFrame is sorted by date.
    """
    out = sort_and_cast_ohlcv(df)
    if price_col not in out.columns:
        raise ValueError(f"Price column '{price_col}' not found.")
    out[out_col] = out[price_col].pct_change()
    return out

def clip_extreme_zscores(df: pd.DataFrame, columns: Iterable[str], z: float = 5.0) -> pd.DataFrame:
    """
    Clip extreme z-scores to +/- z to reduce the impact of outliers.
    """
    out = df.copy()
    cols = _ensure_columns(out, columns)
    for c in cols:
        s = out[c].astype(float)
        mu, sd = s.mean(), s.std(ddof=0)
        if sd == 0 or np.isclose(sd, 0.0):
            continue
        zvals = (s - mu) / sd
        out[c] = np.clip(zvals, -z, z)
    return out
