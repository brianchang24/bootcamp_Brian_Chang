# src/features.py
import pandas as pd
import numpy as np

def add_volatility_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add volatility_ratio = (high - low) / close.
    Requires columns: ['high','low','close'].
    Captures relative intraday volatility.
    """
    out = df.copy()
    required = {"high","low","close"}
    missing = required - set(out.columns)
    if missing:
        raise KeyError(f"Missing columns for add_volatility_ratio: {missing}")
    out["volatility_ratio"] = (out["high"] - out["low"]) / out["close"]
    return out

def add_volume_zscore(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add volume_zscore = (volume - mean) / std.
    Requires column: ['volume'].
    Flags unusually high/low trading activity.
    """
    out = df.copy()
    if "volume" not in out.columns:
        raise KeyError("Missing 'volume' for add_volume_zscore")
    mu = out["volume"].mean()
    sigma = out["volume"].std(ddof=0)
    out["volume_zscore"] = (out["volume"] - mu) / (sigma if sigma != 0 else 1.0)
    return out

def add_ret_vol_interaction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ret_vol_interaction = ret_1d * volume_zscore.
    Requires columns: ['ret_1d'] and (precomputed) ['volume_zscore'].
    Combines direction/magnitude of return with abnormal activity.
    """
    out = df.copy()
    if "ret_1d" not in out.columns:
        raise KeyError("Missing 'ret_1d' for add_ret_vol_interaction")
    if "volume_zscore" not in out.columns:
        raise KeyError("Missing 'volume_zscore' (run add_volume_zscore first)")
    out["ret_vol_interaction"] = out["ret_1d"] * out["volume_zscore"]
    return out

def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience wrapper: add all homework features in a safe order.
    Returns a copy with ['volatility_ratio','volume_zscore','ret_vol_interaction'].
    """
    out = add_volatility_ratio(df)
    out = add_volume_zscore(out)
    out = add_ret_vol_interaction(out)
    return out
