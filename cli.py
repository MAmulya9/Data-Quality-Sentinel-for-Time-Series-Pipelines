import os
import json
import csv
import sys
from typing import Optional
import pandas as pd
from .preprocess import read_time_series, dedupe_and_backfill
from .features import compute_missingness, compute_cadence_stats, rolling_level_shift
from .scoring import probabilistic_anomaly_score
from .triage import triage_from_score, policy_card
from .utils import make_output_dirs

def run_file(path: str, out_dir: str, thresholds: dict = None, time_col: Optional[str] = None):
    """
    Process a single CSV file and write findings + cleaned csv.
    Returns worst triage label for that file.
    """
    os.makedirs(out_dir, exist_ok=True)
    make_output_dirs(out_dir)
    df, inferred_time_col = read_time_series(path, time_col=time_col)
    time_used = time_col or inferred_time_col
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    findings = []
    per_col_summary = {}
    cleaned_export = None

    for col in numeric_cols:
        try:
            # Preprocess only needed columns to maintain other metadata
            tmp = df[[time_used, col]].rename(columns={time_used: "time"})
            cleaned = dedupe_and_backfill(tmp, "time", [col])
            missingness = compute_missingness(cleaned)
            cadence = compute_cadence_stats(cleaned, "time")
            shift = rolling_level_shift(cleaned, col)
            score_series = probabilistic_anomaly_score(cleaned[col])
            avg_score = float(score_series.mean()) if len(score_series)>0 else 0.0
            triage = triage_from_score(avg_score, thresholds)
            findings.append({
                "file": os.path.basename(path),
                "column": col,
                "missingness": missingness.get(col) if isinstance(missingness, dict) else None,
                "cadence_median_s": cadence.get("median_s"),
                "max_jump": shift.get("max_jump"),
                "max_z": shift.get("max_z"),
                "avg_anomaly_score": avg_score,
                "triage": triage
            })
            per_col_summary[col] = {"avg_score": avg_score, "triage": triage}
            # build cleaned export by merging columns on time (preserve time col name)
            cleaned = cleaned.rename(columns={"time": time_used})
            if cleaned_export is None:
                cleaned_export = cleaned.copy()
            else:
                # merge on time
                cleaned_export = pd.merge(cleaned_export, cleaned, on=time_used, how="outer")
        except Exception as e:
            findings.append({
                "file": os.path.basename(path),
                "column": col,
                "missingness": None,
                "cadence_median_s": None,
                "max_jump": None,
                "max_z": None,
                "avg_anomaly_score": None,
                "triage": "amber"
            })
            per_col_summary[col] = {"avg_score": None, "triage": "amber"}

    # write findings (append)
    findings_path = os.path.join(out_dir, "dq_findings.csv")
    header = ["file","column","missingness","cadence_median_s","max_jump","max_z","avg_anomaly_score","triage"]
    write_header = not os.path.exists(findings_path)
    with open(findings_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if write_header:
            writer.writeheader()
        for r in findings:
            writer.writerow(r)

    # update dq_summary.json
    summary_path = os.path.join(out_dir, "dq_summary.json")
    existing = {}
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            try:
                existing = json.load(f)
            except:
                existing = {}
    existing[os.path.basename(path)] = {"per_column": per_col_summary, "policy": policy_card()}
    with open(summary_path, "w") as f:
        json.dump(existing, f, indent=2)

    # cleaned export
    if cleaned_export is not None:
        cleaned_p = os.path.join(out_dir, os.path.basename(path).replace(".csv","") + "_cleaned.csv")
        cleaned_export.to_csv(cleaned_p, index=False)

    # determine worst triage
    worst = "green"
    for v in per_col_summary.values():
        t = v.get("triage")
        if t == "red":
            worst = "red"
            break
        if t == "amber" and worst != "red":
            worst = "amber"
    return worst

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Data Quality Sentinel CLI")
    parser.add_argument("--input", "-i", required=True, help="input CSV file or directory containing CSVs")
    parser.add_argument("--out", "-o", required=True, help="output folder")
    parser.add_argument("--green", type=float, default=0.2, help="green threshold (score <= green => green)")
    parser.add_argument("--amber", type=float, default=0.5, help="amber threshold (green < score <= amber => amber)")
    parser.add_argument("--time-col", type=str, default=None, help="explicit time column name (optional)")
    args = parser.parse_args()
    thresholds = {"green": args.green, "amber": args.amber}
    inp = args.input
    files = []
    if os.path.isdir(inp):
        files = [os.path.join(inp, f) for f in sorted(os.listdir(inp)) if f.lower().endswith(".csv")]
    else:
        files = [inp]
    worst_all = "green"
    for f in files:
        w = run_file(f, args.out, thresholds=thresholds, time_col=args.time_col)
        if w == "red":
            worst_all = "red"
            break
        if w == "amber" and worst_all != "red":
            worst_all = "amber"

    # exit codes: 0 green, 1 amber, 2 red
    if worst_all == "green":
        sys.exit(0)
    elif worst_all == "amber":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
