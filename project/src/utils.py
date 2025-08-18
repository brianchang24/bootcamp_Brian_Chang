import pandas as pd

def get_summary_stats(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    """
    Calculate summary statistics (count, mean, std, min, max) for a given value column,
    grouped by a category column.
    """
    return df.groupby(group_col)[value_col].agg(["count", "mean", "std", "min", "max"])
