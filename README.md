# Data-Quality-Sentinel-for-Time-Series-Pipelines
## 📌 Objective
This project implements an **automated Data Quality (DQ) layer** for time-series pipelines.  
The Sentinel system:
- Detects, classifies, and blocks bad data before modelling
- Provides **root-cause hints** with auto-triage labels
- Produces **reproducible artifacts** (`dq_findings.csv`, `dq_summary.json`, plots, reports)
- Is **CI/CD-ready**, emitting pass/fail statuses (`red/amber/green`) to integrate with pipelines

---

## 📂 Project Structure
```
data-quality-sentinel/
│── data/                     # CSV datasets
│── dq_sentinel/              # Python modules
│   │── __init__.py
│   │── preprocessing.py
│   │── feature_engineering.py
│   │── scoring.py
│   │── triage.py
│   │── ci_cd.py
│   │── reporting.py
│── tests/                    # Unit tests (synthetic, seeded runs)
│── artifacts/                # Output: dq_findings.csv, dq_summary.json, plots
│── plots/                    # Visual plots of missingness, seasonality, shifts
│── cleaned_timeseries.csv    # Export after cleaning
│── environment.yml           # Conda environment file
│── requirements.txt          # Pip dependencies
│── policy_card.md            # Assumptions, risks, scope of anomaly scoring
│── report.md                 # Project report
│── main.py                   # CLI entry point
│── README.md                 # (this file)
```

---

## ⚙️ Installation

### Option 1: Conda
```bash
conda env create -f environment.yml
conda activate dq-sentinel
```

### Option 2: Pip
```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
```

---

## 🚀 Usage

Run the full pipeline on a dataset:

```bash
python main.py --data data/sample_timeseries.csv --out artifacts/
```

Outputs:
- `artifacts/dq_findings.csv` → per-row anomaly flags
- `artifacts/dq_summary.json` → summary with status: red/amber/green
- `artifacts/plots/` → charts (missingness, cadence, seasonality shifts)
- `cleaned_timeseries.csv` → final cleaned export

---

## 🧪 Tests

We include **unit tests on synthetic cases** to ensure reproducibility:

```bash
pytest tests/ -v
```

All test runs are **deterministic** using fixed random seeds.

---

## 🛠️ CI/CD Integration

This repo includes a **GitHub Actions workflow** (`.github/workflows/ci.yml`) that:
- Installs dependencies
- Runs unit tests
- Executes the Sentinel pipeline
- Produces a **status (red/amber/green)**

This enables seamless deployment in production MLOps pipelines.

---

## 📑 Deliverables
- ✅ **Reproducible environment** (`requirements.txt` / `environment.yml`)
- ✅ **Step-by-step How-To-Run guide** (this README)
- ✅ **Modules** (`dq_sentinel/*.py`)
- ✅ **DQ artifacts** (`dq_findings.csv`, `dq_summary.json`, `plots/`)
- ✅ **Sanitized export** (`cleaned_timeseries.csv`)
- ✅ **Policy card** (`policy_card.md`)
- ✅ **Project report** (`report.md`)

---

## 🧾 Policy Card (Short Summary)
- **Scope**: Detect data quality issues in time-series data (missing values, outliers, cadence drifts, seasonal shifts).  
- **Assumptions**: Data is time-indexed and continuous; anomalies are probabilistic, not absolute.  
- **Risks**: Overfitting anomaly scoring, false positives, dependency on sampling rate.  

See [`policy_card.md`](policy_card.md) for full details.

---

## 📊 Example Output (Artifacts)

- `dq_findings.csv`

| timestamp   | value | score | label     |
|-------------|-------|-------|-----------|
| 2024-01-01  | 100   | 0.02  | normal    |
| 2024-01-02  | NaN   | 0.91  | missing   |
| 2024-01-03  | 350   | 0.88  | outlier   |

- `dq_summary.json`

```json
{
  "status": "amber",
  "issues": {
    "missing_pct": 5.4,
    "outliers_pct": 2.1,
    "cadence_breaks": 3
  }
}
```

---

## 📌 Next Steps
- Add **custom anomaly detection rules** for domain-specific datasets
- Expand **visual reports** (trend, seasonality decomposition)
- Integrate with **downstream ML model pipelines**

---
