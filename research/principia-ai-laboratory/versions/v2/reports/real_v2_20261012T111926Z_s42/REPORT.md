# Principia AI Lab V2: Independent Empirical Replication

**Not a proof of a universal law.** Forecaster predictions on held-out datasets and architectures.

**Research phase: exploratory_development.** The bundled datasets were observed during model development. Treat them as exploratory, NOT confirmatory preregistered evidence.

Seeds per dataset: 20 · dataset count: 4 · observations: 1920 · excluded failed runs: 0

Prospective planning for *future* studies: MDE 4.0% · assumed paired SD 5.0% · Holm family alpha 0.05 · minimum planned seeds 20

Planned seed requirement met: **True**

## Held-out predictive tests

| Generalisation test | Candidate MAE | Constant baseline | Probe-only baseline | vs probe (positive preferred) |
|---|---:|---:|---:|---:|
| unseen_dataset | 0.0936 | 0.1570 | 0.1039 | +0.0103 |
| unseen_architecture | 0.1231 | 0.1704 | 0.1039 | -0.0193 |
| unseen_both | 0.1124 | 0.1713 | 0.1039 | -0.0086 |

### Uncertainty around improvement over probe-only baseline

| Holdout | Gain (positive preferred) | Approximate 95% cluster CI | Cluster count |
|---|---:|---:|---:|
| unseen_dataset | +0.0103 | [+0.003, +0.018] | 4 |
| unseen_architecture | -0.0193 | [-0.080, +0.041] | 4 |
| unseen_both | -0.0086 | [-0.016, -0.001] | 4 |

## Release-protocol primary hypotheses (development data; not prospectively confirmed)

| ID | Effect (accuracy points) | 95% CI across datasets | Holm p | Verdict |
|---|---:|---:|---:|---|
| R01 | -0.0559 | [-0.107, -0.005] | 0.980 | opposite_direction |
| R02 | +0.0554 | [+0.008, +0.103] | 0.063 | not_confirmed |
| R03 | +0.1263 | [+0.021, +0.231] | 0.063 | not_confirmed |
| R04 | +0.0166 | [-0.021, +0.054] | 0.252 | effect_below_predeclared_threshold |

## Provenance and statistical caveats

- Observations come from independent publicly distributed measured datasets, with binary target remappings stated in source.
- OOD here means **feature-median-defined covariate groups**, not independent hospitals, locations, or collection periods.
- Model fitting and preprocessing never use the labels of either test subset.
- No empirical dataset is assumed to have a known Bayes ceiling.
- Dataset-level cluster intervals (only four datasets by default) are the primary inferential summary; repeated random seeds are not independent real-world domains.
- Four bundled data sources were inspected while designing and tuning the predictor. A genuine prospective confirmation MUST use newly registered, uninspected sources; development results are not confirmatory.
- The normal-approximation power design uses an assumed seed-level SD and does NOT ensure adequate power across the four independent source datasets.
- The mechanism descriptors use known intervention settings and a cross-validated learnability estimate from labeled TRAIN samples; they are not available for completely unlabeled new tasks.
- The candidate law has been allowed to probe each unseen architecture on training-only labels; this is NOT zero-shot architecture prediction. Probe-only accuracy is separately reported as a demanding baseline.
- All per-condition and negative results, including unsuccessful forecasts, remain available in CSV.
- No claim about consciousness, universal general intelligence, architecture-independent emergence or causality is made.
- Dataset choice, hyperparameters, transform mapping and minimum effect sizes are documented in PROTOCOL_FROZEN.json as RELEASE SETTINGS for future replications, not falsely claimed to have been preregistered before model development.
- Selected OpenML datasets (if any) use feature-vocabulary one-hot encoding learned from unlabeled covariates, a transductive choice disclosed in provenance; never interpret this as a fully prospective live deployment.

## Next falsification gate

A credible stronger claim requires more independent families, genuinely observed site/time domains, blinded held-out task registration, and a forecast law that beats baseline with uncertainty intervals across such families.
