# Release 2.0 — Predictive Law Falsification Workbench

- Retains the complete V1 synthetic engine, external CSV evaluator and arithmetic Ollama adapter.
- Introduces a separate real-data suite with 20-seed prospective planning, four measured source families, 4 machine-learning architectures, 3 feedback/sensing regimes, 2 separated evaluation domains and full train/test disjointness.
- Supports optional additional public OpenML datasets and site/year/environment-separated numeric CSVs.
- Estimates train-only architecture performance by diagnostic two-fold cross-validation; this prevents the speculative theory from getting credit for a measurement directly supplied by the experiment. Comparisons include a direct-probe baseline.
- Predicts accuracy under leave-entire-dataset-out, leave-entire-architecture-out and combined holdouts, with nested meta-validation for a correction coefficient including zero.
- Reports effect magnitudes, dataset-cluster 95% intervals, Holm-adjusted one-sided p-values, minimum effect thresholds and *all* negative evidence.
- Adds a separate real text-modality task using the official 20 Newsgroups split and distinct classifiers.
- Adds separate pretrained Ollama model evaluation using a user-supplied question/answer JSONL; optional helper for downloading real GSM8K benchmark data on the user laptop.
- Archives raw observations, forecasts, provenance, protocol settings and failed or excluded experiments for independent review.
- Explicitly marks the four built-in datasets as development-evaluated and thus NOT a new prospective preregistration.
- No online API keys required for default runs. No GPU required for numeric default runs.
