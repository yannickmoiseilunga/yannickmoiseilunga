# Principia AI Laboratory — A Falsifiable Research Programme (V1 → V3)

> **Research status:** exploratory, computationally reproduced on the enclosed configurations; **no universal law of AI is claimed or confirmed**.

**Research question:** Can we forecast a learning system's accuracy when its **data source, architecture, or both** have not previously been observed? Can a law capture *distinguishability of observations*, *ability to transform learned relations*, and *fidelity of correction*?

The project takes a historical cue from Newton's *Principia Mathematica*: definitions → falsifiable propositions → analytical limits → experiments → adverse findings → revised candidate laws. Newton's mechanical laws are **not** asserted to hold for AI.

## In 60 seconds (plain English)

Imagine learning to identify objects from a familiar collection of examples. How well will you do when both the objects and the method you use to identify them change? A good scientific model would **forecast how performance changes**, not merely explain past successes. These three versions try increasingly demanding predictions. They deliberately keep their failures.

- **V1 — What makes an artificial learner succeed or fail?** Twelve controlled synthetic comparisons assess evidence, compositional reasoning, corrections, memory and environmental change. Eleven were consistent with their toy hypotheses; one was inconclusive. Its forecast sometimes violated known Bayes ceilings.
- **V2 — Does that transfer to measured data and unfamiliar learners?** Four independent tabular/image datasets, four learning architectures and 20 random seeds produced 1,920 records. The correction helped with unseen datasets but worsened forecasts for unseen architectures and combined holdouts.
- **V3 — Can a more constrained mathematical law improve transfer?** A conditional law transforms *error odds* rather than directly adding accuracy. On exploratory held-out surveys and learners, its average forecast errors were slightly smaller, but **all three primary comparisons failed the confirmation criterion**. An indistinguishable-world demonstration establishes a genuine impossibility limit for unconstrained universal point forecasts.

## Evidence-first result comparison

Mean absolute forecast error (MAE), **smaller is better**. **V2 and V3 use different experimental source suites: do not treat these numbers as a matched head-to-head competition.**

| Experimental programme | Test | Candidate MAE | Probe-only MAE | Interpretation |
|---|---|---:|---:|---|
| V1 synthetic | Condition-out | 0.2340 (0.1950 Bayes-constrained) | 0.2639 training-mean (not a probe) | Exploratory toy-world evidence; 54 unconstrained Bayes-ceiling violations |
| V2 measured | Unseen dataset | 0.0936 | 0.1039 | Improvement on development-observed datasets |
| V2 measured | Unseen architecture | 0.1231 | 0.1039 | Candidate worse than probe |
| V2 measured | Both unseen | 0.1124 | 0.1039 | Candidate worse than probe |
| V3 transfer | New datasets | 0.0573 | 0.0669 | Gain; not statistically confirmed |
| V3 transfer | New architecture | 0.0693 | 0.0711 | Small gain; not confirmed |
| V3 transfer | Both unseen | 0.0576 | 0.0613 | Gain; not confirmed |

**Important:** Counts of random-seed runs are not counts of independent domains. The named survey sources are small in number. Artificially constructed shifts cannot substitute for genuine future hospitals, factories, dates or geographies.

## Project navigation

| Stage | Executable code | Results | What changed |
|---|---|---|---|
| [V1 — Foundations](versions/v1/README.md) | [`versions/v1/principia`](versions/v1/principia) | [`versions/v1/reports`](versions/v1/reports) | Information ceilings, 12 synthetic hypotheses, first forecasts |
| [V2 — Replication](versions/v2/README.md) | [`versions/v2/principia`](versions/v2/principia) | [`versions/v2/reports`](versions/v2/reports) | 20 seeds, empirical datasets, uncertainty and holdouts |
| [V3 — Information–Transport](versions/v3/README.md) | [`versions/v3/principia/transport_law.py`](versions/v3/principia/transport_law.py) | [`versions/v3/reports`](versions/v3/reports) | Log-odds error transport, frozen earlier fit, adversarial impossibility witness |

## Documentation for evaluators

- [Research design, checks and all negative findings](docs/EVIDENCE_AND_FINDINGS.md)
- [Two-minute interview account and technical questions](docs/INTERVIEW_GUIDE.md)
- [Exact reproduction and environment notes](docs/REPRODUCE.md)
- [Scientific claims, caveats, and independent confirmation gate](docs/RESEARCH_INTEGRITY.md)
- [Version 3 derivation](versions/v3/V3_MATHEMATICAL_DERIVATION.md)
- [Future independent replication plan](versions/v3/NEXT_REPLICATION_PLAN.md)
- [File-integrity hashes](MANIFEST_SHA256.txt)

## Running

The baseline synthetic programme needs only Python 3.10+. Empirical and predictive transfer experiments need the optional dependencies given in each version's `requirements-research.txt`.

For Windows, enter a version folder and execute `install_research.bat` (V2/V3 only), followed by `run.bat`. The browser dashboard uses an available local port. For reproducible command-line runs, see [docs/REPRODUCE.md](docs/REPRODUCE.md).

## Independence, integrity and licensing

This research was developed iteratively with AI assistance. Public datasets and third-party research remain credited in each version's `SOURCES.md`. Included records are from the documented study executions, not independent external peer replication. No paper acceptance, third-party verification, fully external preregistration, universal validity, causal mechanism, or consciousness claim is made. **No explicit open-source licence is assigned; see the repository owner before reuse.**


## Publishing on Windows (fixed)

Use `publish_to_github.bat` from the extracted folder. It invokes `publish_to_github.ps1` directly, detects/installs Git for Windows on request and pauses to show errors. See [`PUBLISHING_ON_WINDOWS.md`](PUBLISHING_ON_WINDOWS.md). Do **not** run `publish_to_github.sh` via a broken WSL launcher.
