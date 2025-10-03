import pandas as pd
from dq_sentinel.preprocess import dedupe_and_backfill
from dq_sentinel.scoring import probabilistic_anomaly_score
from dq_sentinel.triage import triage_from_score

def test_dedupe_and_backfill_constant():
    df = pd.DataFrame({"time": pd.date_range("2020-01-01", periods=5, freq="D"), "val": [1,1,1,1,1]})
    out = dedupe_and_backfill(df, "time", ["val"])
    assert len(out) >= 5

def test_probabilistic_score_constant():
    s = pd.Series([5]*10)
    scores = probabilistic_anomaly_score(s)
    assert scores.max() == 0.0

def test_triage_thresholds():
    assert triage_from_score(0.1, {"green":0.2,"amber":0.5}) == "green"
    assert triage_from_score(0.3, {"green":0.2,"amber":0.5}) == "amber"
    assert triage_from_score(0.9, {"green":0.2,"amber":0.5}) == "red"