import pandas as pd
import numpy as np
from scipy import stats

def probabilistic_anomaly_score(series):
    """
    Convert a numeric series to anomaly scores [0..1].
    Uses empirical z-score and two-sided normal tail probability:
       z = (x - mu)/sd
       p = 2*(1 - Phi(|z|))
       score = 1 - p   (so very extreme => score near 1)
    Returns pandas Series aligned to input index.
    """
    s = pd.Series(series).astype(float)
    s_clean = s.dropna()
    if len(s_clean) < 2:
        return pd.Series([0.0]*len(s), index=s.index)
    mu = s_clean.mean()
    sd = s_clean.std()
    if sd == 0 or np.isnan(sd):
        return pd.Series([0.0]*len(s), index=s.index)
    z = (s - mu)/sd
    p = 2*(1 - stats.norm.cdf(z.abs()))
    score = 1 - p
    return score.fillna(0.0)

def combined_score(missingness_score, cadence_score, level_shift_score, weights=(0.4,0.2,0.4)):
    w_m, w_c, w_l = weights
    return w_m*missingness_score + w_c*cadence_score + w_l*level_shift_score
