# src/analysis.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from .model_io import load_latest_processed, train_model, save_bundle

REPORTS = Path("reports")
REPORTS.mkdir(parents=True, exist_ok=True)

def validate_features(payload: Dict[str, Any], required: List[str]) -> np.ndarray:
    """
    Expect payload like: {"features": {"gap_pct":0.01, "daily_range_pct":0.02, ...}}
    Returns 2D array (1, n_features) ordered per `required`.
    """
    if "features" not in payload or not isinstance(payload["features"], dict):
        raise ValueError("Payload must contain an object 'features' with named keys.")
    feats = payload["features"]
    missing = [f for f in required if f not in feats]
    if missing:
        raise ValueError(f"Missing feature(s): {missing}")
    try:
        row = [float(feats[f]) for f in required]
    except Exception as e:
        raise ValueError(f"All features must be numeric: {e}")
    return np.array(row, dtype=float).reshape(1, -1)

def evaluate_classifier(y_true: np.ndarray, proba_up: np.ndarray, thr: float = 0.5) -> Dict[str, float]:
    y_pred = (proba_up >= thr).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, proba_up)) if len(np.unique(y_true)) > 1 else float("nan")
    }

def plot_pred_vs_threshold(proba_up: np.ndarray, thresholds: np.ndarray, y_true: np.ndarray, outpath: Path) -> Path:
    accs, f1s = [], []
    for t in thresholds:
        y_pred = (proba_up >= t).astype(int)
        accs.append(accuracy_score(y_true, y_pred))
        f1s.append(f1_score(y_true, y_pred, zero_division=0))
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(thresholds, accs, label="Accuracy")
    ax.plot(thresholds, f1s, label="F1")
    ax.set_xlabel("Threshold"); ax.set_ylabel("Score"); ax.set_title("Threshold Sweep")
    ax.legend(); fig.tight_layout()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, dpi=150); plt.close(fig)
    return outpath

def run_full_analysis(threshold: float = 0.44, test_frac: float = 0.2, features: List[str] = None) -> Dict:
    if features is None:
        features = ["gap_pct","daily_range_pct","ma_ratio_5_20","ret_vol_10","volume_z20","rsi_14","macd","macd_signal"]

    # Load data
    df = load_latest_processed()
    df["y_up"] = (df["ret_1d"].shift(-1) > 0).astype(int)
    dfm = df.dropna(subset=features + ["y_up"]).reset_index(drop=True)

    # Time-aware split
    cut = int(len(dfm) * (1 - test_frac))
    train, test = dfm.iloc[:cut], dfm.iloc[cut:]
    X_tr, y_tr = train[features], train["y_up"]
    X_te, y_te = test[features], test["y_up"]

    # Train fresh model & save a versioned copy
    bundle = train_model(df, features=features, threshold=threshold)
    save_bundle(bundle, Path("model/model.pkl"))

    # Predictions on holdout
    proba_up = bundle["pipeline"].predict_proba(X_te)[:,1]
    metrics = evaluate_classifier(y_te.values, proba_up, thr=threshold)

    # Save metrics CSV
    mdf = pd.DataFrame([metrics])
    metrics_path = REPORTS / "full_analysis_metrics.csv"
    mdf.to_csv(metrics_path, index=False)

    # Save threshold sweep chart
    thr_grid = np.linspace(0.2, 0.8, 25)
    chart_path = REPORTS / "threshold_sweep.png"
    plot_pred_vs_threshold(proba_up, thr_grid, y_te.values, chart_path)

    # Save predictions CSV
    out_pred = test[["date"]].copy()
    out_pred["p_up"] = proba_up
    out_pred["y_true"] = y_te.values
    out_pred["y_pred_thr"] = (proba_up >= threshold).astype(int)
    pred_path = REPORTS / "holdout_predictions.csv"
    out_pred.to_csv(pred_path, index=False)

    return {
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "features": features,
        "threshold": float(threshold),
        "metrics_path": str(metrics_path),
        "predictions_path": str(pred_path),
        "chart_path": str(chart_path),
        "metrics": metrics
    }
