# src/utils.py
from typing import Dict, Any, List
import numpy as np

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
