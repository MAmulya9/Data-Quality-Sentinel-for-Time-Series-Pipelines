import os
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from dq_sentinel.cli import run_file
from dq_sentinel.utils import make_output_dirs

def plot_missingness(df, out_png, title=None):
    miss = df.isna().mean()
    plt.figure(figsize=(6,3))
    miss.plot.bar()
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_series(df, time_col, value_col, out_png, title=None):
    plt.figure(figsize=(8,3))
    plt.plot(pd.to_datetime(df[time_col], errors="coerce"), pd.to_numeric(df[value_col], errors="coerce"))
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def run_all(input_folder: str, output_folder: str, time_col: str = None):
    input_folder = str(input_folder)
    output_folder = str(output_folder)
    make_output_dirs(output_folder)
    # clear previous artifacts if present
    findings = os.path.join(output_folder, "dq_findings.csv")
    summary = os.path.join(output_folder, "dq_summary.json")
    if os.path.exists(findings):
        os.remove(findings)
    if os.path.exists(summary):
        os.remove(summary)
    files = sorted([str(p) for p in Path(input_folder).rglob("*.csv")])
    overall_worst = "green"
    for f in files:
        try:
            w = run_file(f, output_folder, time_col=time_col)
            # create quick plots from raw file
            try:
                df = pd.read_csv(f)
                tcandidates = [c for c in df.columns if any(k in c.lower() for k in ("date","time","timestamp","ts","week","day"))]
                tc = time_col or (tcandidates[0] if tcandidates else df.columns[0])
                base = Path(f).stem
                plot_missingness(df, os.path.join(output_folder,"plots", base + "_missingness.png"), title=base + " missingness")
                # plot first numeric
                numcols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                if numcols:
                    plot_series(df, tc, numcols[0], os.path.join(output_folder,"plots", base + "_" + numcols[0] + "_series.png"), title=base)
            except Exception:
                pass
            if w == "red":
                overall_worst = "red"
                break
            if w == "amber" and overall_worst != "red":
                overall_worst = "amber"
        except Exception as e:
            print("Error processing", f, e)
            if overall_worst != "red":
                overall_worst = "amber"
    with open(os.path.join(output_folder, "dq_overall_summary.json"), "w") as f:
        json.dump({"status": overall_worst}, f, indent=2)
    return overall_worst

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_pipeline.py <input_folder> <output_folder> [time_col]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2]
    tc = sys.argv[3] if len(sys.argv) > 3 else None
    status = run_all(inp, out, time_col=tc)
    print("Done. Overall status:", status)
    # exit codes: 0 green, 1 amber, 2 red
    if status == "green":
        sys.exit(0)
    elif status == "amber":
        sys.exit(1)
    else:
        sys.exit(2)
