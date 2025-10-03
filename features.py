import pandas as pd
import numpy as np
from typing import Dict

def compute_missingness(df: pd.DataFrame) -> Dict[str, float]:
    total = len(df)
    if total == 0:
        return {c: 1.0 for c in df.columns}
    return {c: float(df[c].isna().sum())/total for c in df.columns}

def compute_cadence_stats(df: pd.DataFrame, time_col: str) -> Dict[str, float]:
    idx = pd.to_datetime(df[time_col], errors="coerce")
    diffs = idx.diff().dt.total_seconds().dropna()
    if len(diffs) == 0:
        return {"median_s": None, "std_s": None, "min_s": None, "max_s": None}
    return {"median_s": float(diffs.median()), "std_s": float(diffs.std()), "min_s": float(diffs.min()), "max_s": float(diffs.max())}

def rolling_level_shift(df: pd.DataFrame, value_col: str, window: int = 7) -> Dict[str, float]:
    if value_col not in df.columns:
        return {"max_jump": None, "max_z": None}
    s = pd.to_numeric(df[value_col], errors="coerce")
    if s.dropna().empty:
        return {"max_jump": None, "max_z": None}
    roll = s.rolling(window=window, min_periods=1).mean()
    diff = (roll - roll.shift(1)).abs().dropna()
    std = roll.rolling(window=window, min_periods=1).std().replace(0, np.nan)
    z = diff / std
    return {
        "max_jump": float(diff.max()) if not diff.empty else 0.0,
        "max_z": float(z.max()) if not z.empty else 0.0
    }
