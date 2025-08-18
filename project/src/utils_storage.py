from pathlib import Path
from typing import Union
import pandas as pd

def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def detect_format(path: Union[str, Path]) -> str:
    s = str(path).lower()
    if s.endswith(".csv"): return "csv"
    if s.endswith(".parquet") or s.endswith(".pq") or s.endswith(".parq"): return "parquet"
    raise ValueError(f"Unsupported format: {path}")

def write_df(df: pd.DataFrame, path: Union[str, Path]) -> Path:
    path = Path(path)
    ensure_dir(path)
    fmt = detect_format(path)
    if fmt == "csv":
        df.to_csv(path, index=False)
    else:
        try:
            df.to_parquet(path)
        except Exception as e:
            raise RuntimeError("Parquet engine not available. Install 'pyarrow' or 'fastparquet'.") from e
    return path

def read_df(path: Union[str, Path]) -> pd.DataFrame:
    path = Path(path)
    fmt = detect_format(path)
    if fmt == "csv":
        cols = pd.read_csv(path, nrows=0).columns
        parse = ["date"] if "date" in cols else None
        return pd.read_csv(path, parse_dates=parse)
    else:
        try:
            return pd.read_parquet(path)
        except Exception as e:
            raise RuntimeError("Parquet engine not available. Install 'pyarrow' or 'fastparquet'.") from e
