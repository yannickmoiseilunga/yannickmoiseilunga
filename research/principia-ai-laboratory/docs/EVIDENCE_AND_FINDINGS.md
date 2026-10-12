# Experimental evidence, including negative results

## V1 — controlled synthetic tasks
12 hypotheses, 6 seeds, 300 measurements. 11 outcomes consistent with toy hypotheses; H10 weak-to-strong: inconclusive. Forecast MAE: training-mean 0.2639, unconstrained 0.2340, Bayes-constrained 0.1950. **54 forecast observations exceeded known Bayes ceilings before constraint.** See [raw study report](../versions/v1/reports/20261012T103053Z_standard_s42/REPORT.md).

## V2 — real-data development
20 seeds, four publicly distributed datasets, 1,920 measurements. Candidate vs training probe: unseen data 0.0936 vs 0.1039 MAE; unseen architecture 0.1231 vs 0.1039; double unseen 0.1124 vs 0.1039. Of R01–R04, none passed adjusted confirmation criteria. Sources used during model development: exploratory, NOT independently preregistered. Synthetic domain splits based on feature medians do not count as naturally separate hospitals, factories or dates. See [V2 report](../versions/v2/reports/real_v2_20261012T111926Z_s42/REPORT.md).

## V3 — conditional information–transport
The proposed relationship is logit(error_target) = logit(error_train_probe) + λ·βᵀφ. It reduced mean errors in certain exploratory held-out comparisons but had large clustered intervals:
| Holdout | V3 MAE | Probe MAE | 95% CI for gain | Confirmed? |
|---|---:|---:|---|---|
| New datasets | 0.0573 | 0.0669 | [-0.0603,+0.0795] | No |
| New architecture | 0.0693 | 0.0711 | [-0.0136,+0.0174] | No |
| Both unseen | 0.0576 | 0.0613 | [-0.0792,+0.0866] | No |

Specific regressions: ANES96, Digits and RANDHIE. The constructed indistinguishable-world witness gives accuracies 0.9925 and 0.0075 and a point-forecast worst-case absolute error >=0.4925. This is a conditional impossibility result, **not** proof of a new universal AI law. See [V3 report](../versions/v3/reports/transport_v3_20261012T121322Z/REPORT.md).

## Required next falsification
Independent real domains; predeclared source-level effect size and power; code/weight freeze before unsealing labels; holdout source-family uncertainty; controlled checks for negative and causal-shift failures. Do not infer consciousness, general intelligence, or causal universality from toy tasks. A local Ollama adapter exists but the described tabular experiments are not an LLM evaluation.