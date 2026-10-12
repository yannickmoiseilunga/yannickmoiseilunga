# Principia AI Laboratory — Experimental Report

Generated: 2026-10-12T10:30:53.461669+00:00

## Method

Prespecified synthetic tasks; separate training and test observations; identical master seed for controlled comparisons; analytic Bayes ceilings where available; multiple seeds; bootstrap over seed-level paired effects.

## Preregistered hypotheses

| Hypothesis | Estimated effect | 95% bootstrap interval | Outcome |
|---|---:|---:|---|
| H01 No information: the blind engine cannot reliably exceed chance | -0.026 | [-0.038, -0.010] | consistent (exploratory) |
| H02 Better observation improves sensor-based judgement | +0.148 | [+0.129, +0.163] | consistent (exploratory) |
| H03 Composition allows parity relations inaccessible to linear separators | +0.453 | [+0.378, +0.549] | consistent (exploratory) |
| H04 A changed environment can disturb a successful disposition | +0.860 | [+0.854, +0.866] | consistent (exploratory) |
| H05 An inverted reward misaligns correction with truth | +0.857 | [+0.841, +0.871] | consistent (exploratory) |
| H06 Corrected labels outperform corrupted corrections | +0.048 | [+0.042, +0.055] | consistent (exploratory) |
| H07 An additional instrument can improve decisions | +0.181 | [+0.170, +0.193] | consistent (exploratory) |
| H08 Independent reference memory can resolve otherwise hidden identities | +0.454 | [+0.430, +0.484] | consistent (exploratory) |
| H09 Process verification at larger search budgets can beat first attempt | +0.385 | [+0.375, +0.394] | consistent (exploratory) |
| H10 Weak supervision may or may not elicit stronger learned structure | +0.000 | [+0.000, +0.000] | inconclusive |
| H11 Selecting high-confidence predictions can reduce accepted error | +0.049 | [+0.032, +0.067] | consistent (exploratory) |
| H12 Feedback after acting can improve control over a one-shot decision | +0.190 | [+0.181, +0.198] | consistent (exploratory) |

## Hold-out predictive test

Condition-out forecast MAE: 0.2340; Bayes-constrained forecast MAE: 0.1950; training-mean baseline MAE: 0.2639.
Predictions above known Bayes ceiling: 54.
The forecast is learned from other synthetic conditions using architecture, data count, scenario flags and analytic information ceiling. It is *not* an established law; failed predictions are kept.
See `law_forecasts.csv` for each observation and `law_validation.json` for summary.

**Interpretation:** A result marked “consistent” is compatible with a particular hypothesis in this synthetic study, not proof of a universal law.

## Core measurable quantities

1. **Distinguishability**: exact Bayes optimal accuracy and mutual information for discrete generators.
2. **Transformation**: accuracy differences among prior, linear, interaction and small neural engines on parity and sensors.
3. **Correction**: true-world agreement under clean, corrupted and inverted training signals; OOD loss and calibration.

## Limits and further experiments

- Repeat with independent real datasets and domain-separated train/test sets.
- Increase to at least 20 seeds and select sample size by a prospective power analysis.
- Report negative findings and predefine acceptable effect sizes.
- Test pre-trained local models via the optional local adapter; do not mix them with this synthetic study.
- Replicate in other architectures, environments, modalities and feedback schemes.
- Do not infer internal consciousness, general intelligence, or architecture-independent emergence from toy tasks.

## Artefacts

`observations.csv`: one row per architecture/condition/seed; `predictions.csv`: up to 200 sampled held-out predictions per cell (metrics use all examples);
`manifest.json`: pre-registered comparisons; `findings.json`: effect sizes and seed bootstrap intervals.
