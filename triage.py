import json

def triage_from_score(score: float, thresholds: dict = None) -> str:
    """
    thresholds example: {"green":0.2, "amber":0.5}
    score <= green -> green
    green < score <= amber -> amber
    score > amber -> red
    """
    if thresholds is None:
        thresholds = {"green": 0.2, "amber": 0.5}
    if score is None:
        return "amber"
    try:
        s = float(score)
    except Exception:
        s = 1.0
    if s <= thresholds["green"]:
        return "green"
    elif s <= thresholds["amber"]:
        return "amber"
    else:
        return "red"

def policy_card() -> dict:
    return {
        "component": "anomaly_scoring",
        "scope": "Univariate numeric time-series per file/column",
        "assumptions": [
            "Time column can be inferred or provided to CLI",
            "Series are univariate numeric signals measured at regular cadence or near-regular cadence",
            "Simple imputation (ffill/bfill) is acceptable for scoring"
        ],
        "risks": [
            "Seasonal/periodic patterns may be flagged as anomalies by simple z-based detectors",
            "Multivariate anomalies (cross-signals) are not detected",
            "Thresholds need dataset-specific calibration",
            "Timestamp parsing errors will cause incorrect cadence detection"
        ]
    }
