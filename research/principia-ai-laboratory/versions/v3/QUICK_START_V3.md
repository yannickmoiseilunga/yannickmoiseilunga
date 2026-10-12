# Principia AI Laboratory V3 — Quick Start

## Windows
1. Extract `Principia_AI_Laboratory_v3_0.zip` to a writable folder.
2. Install Python 3.10 or newer if needed.
3. Double-click `install_research.bat` once. This installs scikit-learn, numpy, scipy, pandas and statsmodels into `.venv`.
4. Double-click `run.bat`. It opens a browser on `127.0.0.1` using an available port.
5. Choose **Transport Law V3** to run a new 20-seed experiment, or **Experiments** to inspect the included example and download its evidence archive.

## Terminal

    python -m pip install -r requirements-research.txt
    python main.py --transport-study --seeds 20
    python main.py --no-browser --port 0

Outputs are under `reports/transport_v3_*/`: `REPORT.md`, `summary.json`, `all_predictions.csv`, `protocol.json`, `dashboard.json`. Zip archive is in `reports/`.

## Key rules
- V3 has a 20-seed minimum; new seeded runs on the *same sources* are sensitivity checks, not fresh independent scientific replications.
- The predictor was fitted only on the included `frozen_development_v2.csv`. Do not move target labels into the predictor inputs.
- The source-fit uncertainty radius is not a valid coverage certificate for unseen environments; examine the impossibility witness.
- Report all three regimes, including failures, and compare to probe-only.

## Requirements
No internet needed after packages are installed; no API key, GPU or TPU required.
