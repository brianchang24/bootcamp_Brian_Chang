# src/model_io.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

MODEL_PATH = Path("model/model.pkl")
PROC = Path("data/processed")

DEFAULT_FEATURES: List[str] = [
    "gap_pct","daily_range_pct","ma_ratio_5_20",
    "ret_vol_10","volume_z20","rsi_14","macd","macd_signal"
]

def load_latest_processed(pattern: str = "prices_with_tech_features_model*.csv") -> pd.DataFrame:
    cands = sorted(PROC.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"No processed feature files found in {PROC} matching {pattern}")
    df = pd.read_csv(cands[0], parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    df.attrs["source_file"] = cands[0].name
    return df

def build_pipeline() -> Pipeline:
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=2000))
    ])

def train_model(df: pd.DataFrame, features: List[str] = DEFAULT_FEATURES, threshold: float = 0.44) -> Dict:
    df = df.copy()
    df["y_up"] = (df["ret_1d"].shift(-1) > 0).astype(int)
    dfm = df.dropna(subset=features + ["y_up"]).reset_index(drop=True)

    cut = int(len(dfm) * 0.8)
    train = dfm.iloc[:cut]
    X_tr, y_tr = train[features], train["y_up"]

    pipe = build_pipeline()
    pipe.fit(X_tr, y_tr)

    bundle = {
        "pipeline": pipe,
        "features": features,
        "threshold": float(threshold),
        "trained_on": df.attrs.get("source_file", "<unknown>"),
        "version": "1.0.0"
    }
    return bundle

def save_bundle(bundle: Dict, path: Path = MODEL_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    return path

def load_bundle(path: Path = MODEL_PATH) -> Dict:
    return joblib.load(path)

def ensure_model(features: List[str] = DEFAULT_FEATURES, threshold: float = 0.44) -> Dict:
    """
    Load saved model if present; otherwise train from latest processed data and save it.
    """
    if MODEL_PATH.exists():
        return load_bundle(MODEL_PATH)
    df = load_latest_processed()
    bundle = train_model(df, features=features, threshold=threshold)
    save_bundle(bundle, MODEL_PATH)
    return bundle
