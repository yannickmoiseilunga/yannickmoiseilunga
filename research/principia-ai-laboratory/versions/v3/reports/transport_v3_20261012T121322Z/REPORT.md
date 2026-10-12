# Principia V3 — conditional Information-Transport Law

**Status: exploratory; not proof of a universal law.**

V3 candidate is frozen and fitted exclusively on Version 2 development source measurements.

| Evaluation | Train-only probe MAE | V2 MAE | V3 ITL MAE | V3 gain vs probe | 95% CI (source clusters) |
|---|---:|---:|---:|---:|---|
| new_datasets_known_arch (3 sources) | 0.0669 | 0.0669 | 0.0573 | +0.0096 | [-0.0603, +0.0795] |
| new_arch_known_datasets (4 sources) | 0.0711 | 0.0711 | 0.0693 | +0.0019 | [-0.0136, +0.0174] |
| double_unseen (3 sources) | 0.0613 | 0.0613 | 0.0576 | +0.0037 | [-0.0792, +0.0866] |

## Prespecified outcome

Success threshold: >= 0.01 absolute macro MAE improvement over probe AND cluster-level 95% lower bound > 0.

- **new_datasets_known_arch**: not confirmed.
  - anes96: probe=0.0534, ITL=0.0672, V2=0.0534
  - fair: probe=0.0963, ITL=0.0555, V2=0.0963
  - randhie: probe=0.0511, ITL=0.0493, V2=0.0511
- **new_arch_known_datasets**: not confirmed.
  - breast_cancer: probe=0.0633, ITL=0.0546, V2=0.0633
  - digits: probe=0.0543, ITL=0.0668, V2=0.0543
  - iris: probe=0.1074, ITL=0.1005, V2=0.1074
  - wine: probe=0.0595, ITL=0.0551, V2=0.0595
- **double_unseen**: not confirmed.
  - anes96: probe=0.0309, ITL=0.0364, V2=0.0309
  - fair: probe=0.0941, ITL=0.0534, V2=0.0941
  - randhie: probe=0.0588, ITL=0.0830, V2=0.0588

## Impossibility witness

Indistinguishable worlds yield accuracies 0.9925 and 0.0075, enforcing worst-case point-forecast absolute error >= 0.4925.

## Uncertainty audit

In-sample source residual 90th percentile: 0.3367; THIS IS NOT a valid 90% predictive interval for arbitrary unseen conditions.
- new_datasets_known_arch: observed coverage=100.00%
- new_arch_known_datasets: observed coverage=97.92%
- double_unseen: observed coverage=99.86%

## Limitations

- The previously inspected V2 datasets supply all fitted coefficients. No data from these new sources enters candidate fitting.
- Included independently collected surveys do not supply naturally held-out institutions; observational or feature-defined domains are not proof of causal domain robustness.
- 20 random seeds are repeated fits on the same sources, not 20 independent real-world data-generating environments.
- The inference uses a measured two-fold training-only probe of each architecture, not design-only zero-shot inference.
- This conditional candidate cannot identify arbitrary unseen changes in P(Y|X) from X alone.
- Source-fit residual intervals are optimistic and empirical only.
- No conclusions about consciousness or universal artificial intelligence.
