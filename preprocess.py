from typing import Tuple, List
import pandas as pd
import numpy as np

def read_time_series(path: str, time_col: str = None, parse_dates: bool = True) -> Tuple[pd.DataFrame, str]:
    """
    Read CSV and attempt to infer time column if not provided.
    Returns dataframe and name of time column used.
    """
    df = pd.read_csv(path)
    if time_col is None:
        # Guess: look for common time column names
        candidates = [c for c in df.columns if any(k in c.lower() for k in ("date","time","timestamp","ts","day","week"))]
        chosen = None
        for c in candidates:
            try:
                parsed = pd.to_datetime(df[c], errors="coerce")
                if parsed.notna().sum() > 0:
                    chosen = c
                    break
            except Exception:
                continue
        if chosen is None:
            # fallback to first column that parses >0 datetimes
            for c in df.columns:
                try:
                    parsed = pd.to_datetime(df[c], errors="coerce")
                    if parsed.notna().sum() > 0:
                        chosen = c
                        break
                except:
                    continue
        # final fallback: first column
        time_col = chosen or df.columns[0]
    # parse
    if parse_dates:
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.sort_values(time_col).reset_index(drop=True)
    return df, time_col

def dedupe_and_backfill(df: pd.DataFrame, time_col: str, value_cols: List[str], infer_freq: bool = True) -> pd.DataFrame:
    """
    1) drop exact row duplicates
    2) remove duplicate timestamps (keep first)
    3) infer cadence (median diff) and reindex to regular cadence
    4) simple imputation: forward-fill then backward-fill for numeric value_cols
    Returns dataframe with time_col as column (not index).
    """
    df = df.copy()
    if time_col not in df.columns:
        raise ValueError(f"time_col {time_col} not in df")
    # drop exact duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    # ensure time col is datetime
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col])
    df = df.sort_values(time_col)
    # remove duplicate timestamps
    df = df[~df[time_col].duplicated(keep='first')].reset_index(drop=True)
    if len(df) < 2 or not infer_freq:
        return df.reset_index(drop=True)
    # compute median delta in seconds
    diffs = df[time_col].diff().dt.total_seconds().dropna()
    if diffs.empty:
        return df.reset_index(drop=True)
    median_s = int(diffs.median())
    if median_s <= 0:
        return df.reset_index(drop=True)
    # build new index
    try:
        new_idx = pd.date_range(df[time_col].min(), df[time_col].max(), freq=pd.Timedelta(seconds=median_s))
        df_idxed = df.set_index(time_col).reindex(new_idx)
        # impute only provided value columns
        for c in value_cols:
            if c in df_idxed.columns:
                # cast numeric when possible then fill
                if pd.api.types.is_numeric_dtype(df_idxed[c]) or df_idxed[c].dtype == object:
                    # forward then backward fill
                    df_idxed[c] = pd.to_numeric(df_idxed[c], errors="coerce")
                df_idxed[c] = df_idxed[c].fillna(method='ffill').fillna(method='bfill')
        df_idxed = df_idxed.reset_index().rename(columns={'index': time_col})
        return df_idxed
    except Exception:
        return df.reset_index(drop=True)
