# Evidence dossier: hypotheses, figures, adverse results

## V1 — Mechanism-screening stage (synthetic)

- Twelve stated comparisons across 6 seeds, 300 condition/seed/domain observations; 11 consistent with synthetic task hypotheses; **H10 weak-to-strong yielded zero estimated effect and was inconclusive**.
- Forecast MAE: training-mean 0.2639; candidate 0.2340; Bayes-constrained candidate 0.1950. **54 unconstrained predictions surpassed known Bayes ceilings.**
- Synthetic experiments establish controlled mechanisms and counterexamples, **not** architecture-agnostic general intelligence.
- Source: [`../versions/v1/reports/20261012T103053Z_standard_s42/REPORT.md`](../versions/v1/reports/20261012T103053Z_standard_s42/REPORT.md).

## V2 — Real-data development

- 4 public sources, 4 architectures, 3 experimental conditions, 2 evaluation domains, 20 random seeds: 1,920 observations; 0 recorded failed runs.
- Held-out dataset forecast candidate/probe MAE 0.0936/0.1039. **Held-out architecture 0.1231/0.1039**; **double holdout 0.1124/0.1039**.
- R01 pointed in opposite direction (estimated effect -0.0559, adjusted p 0.980); R02 +0.0554 (adjusted p 0.063); R03 +0.1263 (adjusted p 0.063); R04 +0.0166, below predefined 0.04 threshold.
- The predictor and procedures were refined using these datasets: **exploratory, not independent preregistered confirmation**. Group shift is median-feature-defined, not a naturally occurring hospital/site/time separation.
- Source: [`../versions/v2/reports/real_v2_20261012T111926Z_s42/REPORT.md`](../versions/v2/reports/real_v2_20261012T111926Z_s42/REPORT.md).

## V3 — Conditional log-odds transfer

Equation: `logit(error_target) = logit(error_train_probe) + λ · βᵀ φ`.

`φ` uses measured training-only data and unlabeled target properties (where available), including proxy shift, calibration, sensing/correction settings and sample efficiency. Coefficients were fitted on V2 development sources and evaluated on separate survey sources and architecture comparisons.

| Holdout | V3 MAE | Probe MAE | Gain | 95% source-cluster CI | Confirmation? |
|---|---:|---:|---:|---|---|
| New sources, familiar architecture | 0.0573 | 0.0669 | +0.0096 | [-0.0603, +0.0795] | **No** |
| New architecture, familiar sources | 0.0693 | 0.0711 | +0.0019 | [-0.0136, +0.0174] | **No** |
| Both unseen | 0.0576 | 0.0613 | +0.0037 | [-0.0792, +0.0866] | **No** |

Success required at least 0.010 absolute gain and a strictly positive lower cluster CI. Dataset failures **ANES96, Digits, and RANDHIE** are retained rather than deleted.

**Impossibility witness:** identical training evidence and observable target inputs led to accuracies 0.9925 and 0.0075 across two internally different worlds. A fixed forecast must incur worst-case absolute error of at least 0.4925. This supports a logical impossibility claim under unrestricted concept shifts, not a new universal mathematical formula for all AI.

- Source: [`../versions/v3/reports/transport_v3_20261012T121322Z/REPORT.md`](../versions/v3/reports/transport_v3_20261012T121322Z/REPORT.md).

## What evidence would change the conclusion?

1. Freeze both candidate and comparator before inspecting new sources.
2. Obtain 20+ genuinely independent domains/source families (20 random seeds alone does not provide this).
3. Register the samples and minimum detectable difference prospectively at the domain-cluster level.
4. Test different architectures **without** fine-tuning forecasts after examining their held-out labels.
5. Confirm a useful improvement **with source-cluster confidence intervals excluding zero**, not just a better pooled average.
6. Independently reproduce results on another machine and verify dataset versioning and checksums.
