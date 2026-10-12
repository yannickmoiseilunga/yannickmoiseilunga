# Principia AI Laboratory · Version 3.0

**New:** Conditional Information–Transport Law predicting changes in classification accuracy across environments and architectures.

Windows: run `install_research.bat`, then `run.bat` and open the **Transport Law V3** tab. The interactive dashboard runs the full study and displays failed/negative findings.

CLI: `python main.py --transport-study --seeds 20`.

Requires Python 3.10+, requirements-research.txt. V3 offline external data come from statsmodels and are installed as part of optional research requirements. No GPU or API token required.

V3 reuses frozen V2 training observations and retains V2 synthetic, empirical, text and local Ollama capabilities. All fitted coefficients are trained exclusively on the supplied V2 development observations. V3 provides no guarantee of architecture-independent predictions, and an exact concept-shift non-identifiability test proves the limits of unconditional universal forecasting.

See `V3_PROTOCOL_FROZEN.md`, `V3_MATHEMATICAL_DERIVATION.md`, `IMPLEMENTATION_NOTES.md`, and `reports/transport_v3_*/REPORT.md`.

---

# Version 2: Real-world prediction and independent replication

**Start here: [QUICK_START_V2.md](QUICK_START_V2.md).** This release keeps the previous synthetic laboratory but adds a separate 20-seed real-data programme, entire-dataset and entire-architecture holdouts, an independent text-modality track, an optional real JSONL/Ollama track, public dataset imports, and a candidate law compared against a strong training-only diagnostic baseline. **The bundled demonstration is exploratory and does not prove the general corollary.** See [RESEARCH_METHODS_V2.md](RESEARCH_METHODS_V2.md), [CLOUD_OPTIONS.md](CLOUD_OPTIONS.md), and [RELEASE_NOTES_V2.md](RELEASE_NOTES_V2.md).

Windows: first run `install_research.bat`, then `run.bat`. macOS/Linux: `./install_research.sh` then `./run.sh`. To repeat the included development study: `python main.py --real-study --seeds 20`. 

---

# Principia AI Laboratory

**Executable experimental research workbench** exploring the proposed *Corollarium Generale — De Limitibus et Augmento Intelligentiae Artificialis*.

This is an independently implemented research prototype. It is **not affiliated with Isaac Newton, OpenAI, Google DeepMind, or the authors of the cited publications**. The Newtonian structure and proposed universal corollary are original hypotheses, not claims contained in *Principia Mathematica*. Mathematical limits under explicit assumptions differ from general empirical propositions about all AI systems.

## Requirements and first run

- Windows, macOS, or Linux and **Python 3.10 or newer**.
- No `pip install`, GPU, model download, token, internet connection, or paid API required.

On Windows, extract the zip and **double-click `run.bat`**. On macOS/Linux, run `./run.sh`. The programme finds an available local port, opens a browser if the operating system permits, and announces the local URL in its console. If the browser does not open automatically, copy the printed `http://127.0.0.1:<port>` address. The server binds only to `127.0.0.1`.

Press **Run the experiments** to execute one of these presets:

| Preset | Independent seeds | Typical held-out observations per cell | Goal |
|---|---:|---:|---|
| Quick | 3 | 300 | Smoke-test and explore methods |
| Standard | 6 | 600 | Compare robustness |
| Extended | 20 | 1,200 | Stronger seed-level uncertainty estimate |

The dashboard displays a progress bar and preserves **separate, timestamped outputs** in `reports/`. Failed studies surface an error instead of entering an infinite loading state.

You can also run in a terminal:

```shell
python main.py --run --preset quick --seed 42
python main.py --run --preset extended --seed 42
python main.py --no-browser --port 0
python -m unittest discover -s tests -v
```

## What the programme measures

Each synthetic world has hidden **ground truth** and a separate observation channel. The engine never receives the hidden truth at test time. The benchmark has 12 preregistered comparisons, and a wider experimental atlas covering:

1. **Indistinguishability**: an unobserved random bit; the analytic Bayes ceiling is exactly 50%.
2. **Quantity of impression**: one versus two versus three independent noisy observations; exact mutual information.
3. **Composition and architectural power**: XOR relation and differing representation abilities of majority-prior, linear logit, pairwise-interaction logit and one-hidden-layer neural classifiers.
4. **Model size and dataset size**: fixed-size architectural comparisons with 48, medium and full-size samples; recorded parameter/operation counts (small-scale adaptation of scaling-law methodology, not a Chinchilla replication).
5. **Resistance/shift**: a strongly predictive spurious feature during training changes reliability in the test environment (WILDS-style split).
6. **Objective versus truth**: clean reward, corrupted labels and a fully inverted reward objective.
7. **Uncertainty**: Brier, log loss, expected calibration error and accuracy at highest-confidence 80% coverage.
8. **Memory and external evidence**: hidden random entity values and retrieval of an independent exact registry.
9. **Sequential reasoning**: stochastic multi-stage arithmetic candidates, noisy process and outcome verifiers, and best-of-1/4/16 search (inspired by process supervision).
10. **Weak-to-strong**: weak linear teacher labels for a more expressive student, compared with true supervised and weak teacher controls. This often **fails to help**; there is no programmed success condition.
11. **Reciprocal action and feedback**: a controllable binary world with an imperfect observation, fallible action and improved post-action measurement.
12. **Apparent intelligence**: prediction agreement between different architectures on the same unseen observations.
13. **Self-reference**: repeated pseudo-labelling using a model's own guesses, evaluated against unchanged ground truth.
14. **Out-of-condition forecasts**: a fitted ridge candidate forecast of accuracy for each entirely held-out experimental condition, with MAE compared against a training-mean baseline and measured violations of known Bayes ceilings.

### Core measurable quantities

| Quantity | Observed/estimated implementation | Limitation |
|---|---|---|
| Distinguishability | Exact enumerated Bayes-optimal accuracy and `I(World; observations)` in bits | Only known finite synthetic distributions |
| Transformational power | Held-out generalisation on linearly inseparable relations; model comparison/ablation | No general theory of all possible architectures |
| Correction versus reality | Held-out accuracy, Brier, log loss under clean, corrupted, inverted labels | Strong causal claims only inside synthetic randomised generators |
| Prediction | Condition-held-out forecast MAE, baseline MAE, ceiling violations | Phenomenological regression is a **candidate**, not a proven law |

### Scientific honesty

Synthetic demonstrations **cannot prove universal laws about all artificial intelligence**, nor can all of Newton's postulated terms be made measurable without adding operational assumptions. A theoretical impossibility result **is** provable given an indistinguishable observation channel and the assumption that no hidden side-channel exists. Several other propositions can only be *supported or falsified in tested model families*.

Status `consistent (exploratory)` means that a seed-bootstrap interval met a prespecified numerical condition on the synthetic benchmark. It is not a frequentist equivalence test, a replicable p-value or a claim of real-world proof. Seed bootstrap intervals alone omit major sources of uncertainty; use independent datasets and additional seeds.

### Independent real-world data

On the **Independent evidence** tab, load a CSV with a `0/1` target and **numeric** predictor columns. A domain column enables holding out an entire site/year/domain. Standardisation fits on **training rows only**. Training is capped at 3,000 rows to protect laptop resources; held-out metrics cover the full test set. CSV evaluation does not infer causal identifiability or the exact Bayes ceiling.

CLI:

```shell
python main.py --csv my_data.csv --target label
python main.py --csv my_data.csv --target label --domain region --train-domain north
```

If Ollama is already installed with a local model, choose **Detect local models** in the interface, or run:

```shell
python main.py --ollama llama3.2:3b --items 20
```

This adapter connects to `127.0.0.1:11434` (local Ollama only) and grades constrained arithmetic with exact answers. It does **not** secretly download a model, connect to a third-party API, or claim arithmetic is a general AI evaluation.

## What the exported study contains

- `manifest.json`: configuration, seed, preregistered hypotheses, corollary mappings, limitations.
- `observations.csv`: **all** per-seed/condition/test-set metrics.
- `predictions.csv`: reproducible sample of up to 200 individual held-out predictions per cell. Full metrics use the entire test set; sampling keeps extended runs laptop-safe.
- `findings.json`: hypothesis effects and seed bootstrap intervals.
- `law_forecasts.csv`: blind condition-held-out forecasts and prediction errors.
- `law_validation.json`: summary forecast performance and Bayes ceiling violations.
- `REPORT.md`: readable evidence report. `dashboard.json`: reusable dashboard content.
- A ZIP archive of each timestamped run is available through **Export evidence**.

Output directories are not overwritten, even when a study is repeated using the same seed. The programme stores CSV data only in a local `reports/uploads` directory when uploaded using the browser.

## Project structure

```
main.py                     entry point and CLI
run.bat / run.sh            Windows / Unix launchers
principia/worlds.py         ground-truth generators and exact information limits
principia/models.py         pure-Python logistic/interactions/MLP learners
principia/experiments.py    preregistered controlled interventions and simulations
principia/metrics.py        scoring, calibration and seed bootstrap
principia/prediction.py     leave-one-condition-out forecast model
principia/reporting.py      versioned reports and machine-readable evidence
principia/external.py       independent CSV and optional local Ollama adapters
principia/webapp.py         loopback HTTP server and job management
static/                     responsive interactive local laboratory
RESEARCH_METHODS.md         detailed methods, connections, and failure criteria
SOURCES.md                  research references and URLs
tests/                      executable self-tests
```

## Next research requirements

To elevate the project beyond the toy setting: add prospective power analysis; use genuinely independent real-world datasets; test multimodal and agentic models under the same preregistered observation/feedback interventions; validate theoretical information bounds for partially observed dynamic systems; independently reproduce numerical findings on more architectures; and demonstrate accurate predictions of *unseen families* before attempting a general law of intelligence.
