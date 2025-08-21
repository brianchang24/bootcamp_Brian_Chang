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
    out = df.copy()
    # Only parse if not already datetime-like
    if "date" in out.columns and not pd.api.types.is_datetime64_any_dtype(out["date"]):
        s = out["date"].astype(str).str.strip()
        # try tz-aware first, then fallback
        dt = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S%z", errors="coerce")
        dt = dt.fillna(pd.to_datetime(s, errors="coerce", utc=False))
        out["date"] = dt
    if "date" in out.columns:
        out = out.sort_values("date", kind="mergesort").reset_index(drop=True)

    for c in ["open","high","low","close"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    if "volume" in out.columns:
        out["volume"] = pd.to_numeric(out["volume"], errors="coerce").astype("Int64")
    return out


def ffill_ohlcv_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Forward-fill small gaps for OHLCV columns.
    Assumes 'date' already parsed & df already sorted by 'date'.
    """
    out = df.copy()
    cols = [c for c in ["open","high","low","close","volume"] if c in out.columns]
    out[cols] = out[cols].ffill()
    return out

def add_returns(df: pd.DataFrame, price_col: str = "close",
                ret_col: str = "ret_1d", ret_z_col: str = "ret_1d_z") -> pd.DataFrame:
    """
    Adds raw 1-day return (percent) and its z-score as new columns.
    Does not clip/winsorize; that’s handled separately.
    """
    out = df.copy()
    if price_col not in out.columns:
        raise ValueError(f"Price column '{price_col}' not found.")
    out[ret_col] = out[price_col].pct_change() * 100.0  # % return
    # z-score only where ret is not NaN
    mu = out[ret_col].mean(skipna=True)
    sd = out[ret_col].std(ddof=0, skipna=True)
    out[ret_z_col] = (out[ret_col] - mu) / sd if sd and sd != 0 else np.nan
    return out

def winsorize_zscores(df: pd.DataFrame, columns, z: float = 5.0) -> pd.DataFrame:
    """
    Winsorize (cap) z-score columns at ±z. Keeps rows; modifies only *_z columns.
    Example: columns=["ret_1d"]  --> caps 'ret_1d_z' to [-z, z].
    """
    out = df.copy()
    for col in columns:
        z_col = f"{col}_z"
        if z_col not in out.columns:
            # silently skip if z column not present
            continue
        out[z_col] = out[z_col].clip(lower=-z, upper=z)
    return out

def add_daily_range(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily_range = high - low."""
    if {"high", "low"} <= set(df.columns):
        df["daily_range"] = df["high"] - df["low"]
    return df

def add_gap(df: pd.DataFrame) -> pd.DataFrame:
    """Add gap = (open - prev_close) / prev_close."""
    if {"open", "close"} <= set(df.columns):
        df["gap"] = (df["open"] - df["close"].shift(1)) / df["close"].shift(1)
    return df
