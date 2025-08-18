# project/src/ingest_api.py
from pathlib import Path
from datetime import datetime
import os, json
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

def ts(): return datetime.now().strftime("%Y%m%d-%H%M")

def run(ticker: str, out_dir: Path):
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = yf.Ticker(ticker).history(period="1y", interval="1d").reset_index()
    df = df.rename(columns={"Date":"date","Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
    df["date"] = pd.to_datetime(df["date"])
    for c in ["open","high","low","close"]: df[c] = pd.to_numeric(df[c], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").astype("Int64")
    path = out_dir / f"api_yfinance_{ticker}_{ts()}.csv"
    df.to_csv(path, index=False)
    return path

if __name__ == "__main__":
    out = run(os.getenv("TICKER", "AAPL"), Path(__file__).resolve().parents[1] / "data" / "raw")
    print("Saved:", out)
