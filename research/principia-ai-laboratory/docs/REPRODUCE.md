# Reproducibility guide

## Requirements

- Python >=3.10. CPU-only baseline works without a GPU or network.
- V2/V3 empirical experiments use the optional research packages in `requirements-research.txt`. Optional OpenML and GSM8K downloads require network access and their own provenance.
- Results shipped in `versions/vN/reports/` document the **recorded prior runs**. A new run writes new timestamps and may differ across software/platform versions.

## Step 1 — rerun unit tests

```bash
cd versions/v1 && python -m unittest discover -s tests
cd ../v2 && python -m unittest discover -s tests
cd ../v3 && python -m unittest discover -s tests
```

## Step 2 — rerun V1 synthetic programme

```bash
cd versions/v1
python main.py --help
python main.py --no-browser   # consult --help for release-specific arguments
```

## Step 3 — rerun V2 real data (CPU)

```bash
cd versions/v2
python -m pip install -r requirements-research.txt
python main.py --real-study --seeds 20
```

## Step 4 — rerun V3 transfer (CPU)

```bash
cd versions/v3
python -m pip install -r requirements-research.txt
python main.py --help
```

Consult [`versions/v3/QUICK_START_V3.md`](../versions/v3/QUICK_START_V3.md) for exact command combinations, preloaded V2 development data, transport-law plots and experiment-mode options. Commands must be run within the specific version directory.

## Provenance and failure logging

- Compare the included `REPORT.md`, `protocol.json`/`PROTOCOL_FROZEN.json`, raw `*.csv`, and `manifest.json`.
- Track data source licenses and dataset versions; avoid presenting built-in scikit-learn source groups as naturally independent institutions.
- Count *independent source families*, not simply runs, when reporting confidence intervals.
- Never suppress failed source groups or adverse effects to improve summary statistics.

## Local pre-trained LLM benchmarking

The V2/V3 Ollama adapter supports a separately reported language-model benchmark with explicit model tag, prompt, dataset source and seed. It was not run as part of the enclosed 1,920-measurement tabular study and should not be pooled with those results.
