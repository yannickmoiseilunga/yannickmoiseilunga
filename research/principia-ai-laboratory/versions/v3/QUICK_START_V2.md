# Principia AI Laboratory V2 — Laptop quick start

## Windows: first-time installation

1. Install Python 3.10+ from python.org with **Add Python to PATH** enabled.
2. Unzip the package into a local folder, not a OneDrive/cloud-synchronised path if possible.
3. Double-click **`install_research.bat`** once. This installs numpy, scipy, scikit-learn and pandas into the project's own `.venv`.
4. Double-click **`run.bat`**. The dashboard starts at a local `127.0.0.1` port chosen automatically. No fixed port such as 8501 is assumed.
5. Select **Empirical V2**. With the bundled four offline datasets checked and 20 seeds selected, click **Run real-data study**.
6. In **Experiment ledger**, select a saved `real_v2_...` run and export the run ZIP. On the V2 page, inspect the negative findings and three held-out forecast regimes.

macOS/Linux: `chmod +x install_research.sh run.sh && ./install_research.sh && ./run.sh`.

## Command line

```sh
python main.py --real-study --seeds 20 --seed 42
python main.py --real-study --seeds 30 --datasets breast_cancer,wine,iris,digits,openml_diabetes,openml_credit_g
python main.py --real-study --seeds 20 --real-csv own_observations.csv --real-target label --real-domain site --real-base plant_A
python main.py --text-study --seeds 20
python main.py --local-benchmark data/gsm8k_test.jsonl --model qwen3:4b --items 50
```

When using the isolated `.venv`, replace `python` with `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on macOS/Linux.

### Dataset rules

Four bundled datasets work entirely offline once scikit-learn is installed. OpenML choices (data IDs 37, 31, 1590) require internet on the first run and are cached. `--text-study` likewise downloads 20 Newsgroups once. Public data are used under their own terms; the ZIP does not redistribute upstream raw data.

For a more meaningful real domain shift, import a numeric CSV with `label`=0/1 and a column such as `site`, `year`, `machine`, `hospital`, or `instrument`. Specify the training site and hold out the remaining sites. This is strictly stronger evidence of site transfer than a synthetic median-based subgroup.

### Pretrained language models without an API key

Install [Ollama](https://ollama.com/) and a small local model, for instance a model your hardware can hold in RAM. Run `ollama list` to see installed tags, then specify one of those tags exactly.

For the public GSM8K real-question benchmark, separately install Hugging Face datasets: `python -m pip install datasets`, then run `python download_public_gsm8k.py`. The real benchmark is downloaded *on your machine*, not included in the package. Check upstream dataset license/terms. Finally use `--local-benchmark data/gsm8k_test.jsonl --model <tag> --items 50`. This does not fine-tune any model.

**Do not pool** those results with the synthetic experiment outcomes. Every track saves an independent report folder and evidence ZIP.

## Costs and suitable computers

The four default numeric studies are designed for an ordinary laptop and do not use CUDA, a TPU or a rented GPU. In development they completed 20 seeds and four datasets in approximately 11 seconds on the available execution environment, which is **not** an estimate for your specific computer. Start locally and judge your own runtime.

The optional text benchmark, multiple OpenML tasks and especially local language-model inference can demand more memory and computation. GPU rentals become relevant for large language-model inference or fine-tuning, not for the scikit-learn CPU pipeline. Consult `CLOUD_OPTIONS.md` before purchasing compute.

## Interpretation

Included demonstrations are **exploratory**, not prospective proof. They were used to shape this release. A decisive validation requires new uninspected datasets and genuinely independent observed domains under a timestamped locked protocol. In particular, the train-only architecture-probe baseline is difficult to beat, and the V2 law's architecture-generalisation improvements have **not** been established.
