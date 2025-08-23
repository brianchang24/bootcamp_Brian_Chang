# src/features.py
from __future__ import annotations
import pandas as pd
import numpy as np

def _ensure_datetime_tz(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    out = df.copy()
    if col not in out.columns:
        raise KeyError(f"Expected a '{col}' column in prices DataFrame.")
    out[col] = pd.to_datetime(out[col], errors="coerce", utc=True)
    return out

def _rsi(series: pd.Series, n: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    roll_down = down.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = roll_up / roll_down
    return 100 - (100 / (1 + rs))

def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add common, reproducible daily features from OHLCV.
    Requires columns: date, open, high, low, close, volume.
    Returns a copy with new feature columns (NaNs are expected at the start of rolling windows).
    """
    out = _ensure_datetime_tz(df).sort_values("date").reset_index(drop=True)

    # Gap vs prior close (market-open surprise)
    out["gap_pct"] = out["open"] / out["close"].shift(1) - 1

    # Intraday volatility proxy
    out["daily_range_pct"] = (out["high"] - out["low"]) / out["close"].replace(0, np.nan)

    # Moving averages & ratio (5 vs 20)
    out["ma_5"] = out["close"].rolling(5).mean()
    out["ma_20"] = out["close"].rolling(20).mean()
    out["ma_ratio_5_20"] = out["ma_5"] / out["ma_20"] - 1

    # Rolling volatility of returns (10-day)
    out["ret_vol_10"] = out["ret_1d"].rolling(10).std()

    # Volume surprise (z-score over 20 days)
    vol_mean_20 = out["volume"].rolling(20).mean()
    vol_std_20 = out["volume"].rolling(20).std()
    out["volume_z20"] = (out["volume"] - vol_mean_20) / vol_std_20

    # RSI(14)
    out["rsi_14"] = _rsi(out["close"], 14)

    # MACD (12,26,9)
    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()

    return out

def select_model_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep a compact modeling table (drop rows with NaNs from rolling windows).
    """
    cols = [
        "date", "ret_1d", "ret_1d_z",
        "gap_pct", "daily_range_pct",
        "ma_ratio_5_20", "ret_vol_10",
        "volume_z20", "rsi_14",
        "macd", "macd_signal",
    ]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns for modeling dataset: {missing}")
    return df[cols].dropna().reset_index(drop=True)
