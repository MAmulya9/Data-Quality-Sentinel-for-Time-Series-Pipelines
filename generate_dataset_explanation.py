import pandas as pd
from pathlib import Path
import argparse

def explain_folder(folder: str, out_md: str = "DATASET_EXPLANATION.md"):
    p = Path(folder)
    md = ["# Dataset folder explanation\n"]
    files = sorted(p.rglob("*.csv"))
    for f in files:
        try:
            df = pd.read_csv(f, nrows=200)
            cols = df.columns.tolist()
            # guess time column
            time_candidates = [c for c in cols if any(k in c.lower() for k in ("date","time","timestamp","ts","week","day"))]
            time_col = None
            for c in time_candidates:
                try:
                    parsed = pd.to_datetime(df[c], errors="coerce")
                    if parsed.notna().sum() > 0:
                        time_col = c
                        break
                except:
                    continue
            numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
            md.append(f"## File: `{f.relative_to(p)}`")
            md.append(f"- Columns: {cols}")
            md.append(f"- Inferred time column (candidate): `{time_col}`")
            md.append(f"- Numeric columns: {numeric_cols}")
            md.append("- Preview rows (first 5):")
            preview = df.head(5).to_dict(orient="records")
            for row in preview:
                md.append(f"  - {row}")
            md.append("")
        except Exception as e:
            md.append(f"## File: `{f.relative_to(p)}`")
            md.append(f"- Error reading file: {e}\n")
    Path(out_md).write_text("\n".join(md))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="folder with CSVs to describe")
    parser.add_argument("--out", default="DATASET_EXPLANATION.md")
    args = parser.parse_args()
    explain_folder(args.folder, args.out)
    print("Wrote", args.out)
