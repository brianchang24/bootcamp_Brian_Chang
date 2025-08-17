import pandas as pd

def get_summary_stats(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """Return grouped summary stats (count, mean, std, min, max)."""
    return df.groupby(group_col, as_index=False)[value_col].agg(["count","mean","std","min","max"])
