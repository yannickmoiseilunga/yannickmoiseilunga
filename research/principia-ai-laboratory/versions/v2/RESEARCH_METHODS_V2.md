# Principia AI Laboratory V2 — Formal experimental methodology

## Research question

Can a mathematical relation constructed from **distinguishability** (train-only diagnostic learnability), **transformation capability** (a prespecified description of the architecture), and **correction quality** (observed-label fidelity, sensing damage and measured covariate shift) predict an engine's final test accuracy for **datasets and/or architectures entirely absent from meta-model fitting**?

This question is harder than describing observed behaviour after fitting. V2 is designed to publish failed predictions and rival baselines, not to manufacture universal agreement.

## What was built and what remains unproved

- Real measured classification sources: built-in Wisconsin breast cancer (tabular), UCI Wine (tabular), Fisher Iris (tabular), and optical handwritten digits (8×8 image pixels). Their observations are real, but their binary target choices are research design decisions.
- Optional additional datasets via OpenML 37, 31 and 1590, downloaded and cached only when selected. Their source labels and exact metadata must be checked before publication. Optional user CSV permits explicit real site/year/domain holdouts.
- Fixed learners: a prior-only dummy, penalised logistic regression, a regularised decision tree, and random Fourier features followed by penalised logistic regression. These are genuinely distinct computational structures, but none is a frontier LLM.
- Three prespecified learning/sensing regimes: clean ground truth, 20% label flips, and 40% random feature masking. The latter two are experimentally *introduced* interventions on genuine measured inputs, not natural corruption measured at a collection site.
- Domain shift: in built-in sets, the split is based on an observed feature median, with all high-group cases excluded from training and an in-group IID holdout from the low-group. This IS a domain-separated train/test comparison, but it is NOT independent hospital/writer/geography data. External CSV can supply genuinely observed site/time groups.
- The model predicts accuracy; it does not predict consciousness, architecture-independent emergence, subjective experience, general intelligence, physical FLOPs or a universal Bayes ceiling.

## Prospectively declared quantities and power

`principia.real_study.PROTOCOL` contains primary hypotheses, intervention magnitudes, architectures, target metric, and acceptance thresholds. The generated `PROTOCOL_FROZEN.json` and `power_analysis.json` preserve these settings for each run.

The sample-size planning function is an *assumption-based*, normal-approximation, one-sided paired test:

```
n = ceil((z(1-alpha/k) + z(power))^2 * (assumed_sd / MDE)^2)
chosen_seeds = max(20, n)
```

Defaults: family alpha 0.05, four planned comparisons, power 0.80, MDE 0.04 absolute accuracy points, assumed seed-wise paired effect SD 0.05. This yields at most the requested minimum of 20 seeds. This calculation **does not imply** 80% power for hypotheses about independent data-generating environments: default is only four distinct datasets, and dataset-level clustered t inference has very limited degrees of freedom. More genuinely independent collection domains are needed, not just more seeds.

### Primary comparisons

| ID | Paired outcome comparison | MDE |
|---|---|---|
| R01 | RBF random Fourier features versus linear regression, clean IID accuracy | +0.04 |
| R02 | Clean versus 20% corrupted training labels, linear IID | +0.04 |
| R03 | Full features versus 40% feature-dropout, linear IID | +0.04 |
| R04 | Same trained linear model evaluated IID versus feature-defined OOD, clean | +0.04 |

Positive effects are prespecified; negative results are legitimate findings. p-values are obtained from four **dataset-level** mean effects (not treating 20 seed replications as 80 independent source datasets); Holm step-down adjustment controls the family. Confidence intervals are 95% t intervals over dataset mean effects, and interpretations remain fragile with four clusters. Positive effects below the stated minimum are reported separately from robustly supported effects. Do not treat an inconclusive test as an equivalence demonstration.

**Research transparency:** The four bundled datasets were inspected during the development of the meta-predictor, including choice of features and shrinkage. Hence the included V2 demo is **exploratory development**, despite containing a frozen *release* protocol. Calling it a prospective preregistered confirmation would be incorrect. Independently sourced, uninspected future datasets must be enrolled under a timestamped protocol before accessing their labels to make a confirmation claim. The exact domain/protocol fingerprints are in run manifests.

## Nonleaking diagnostics and mathematical candidate

For each dataset/seed, the numeric model is fitted only on the low-feature-domain subset. Training-only cross-validation provides two observable quantities:

- `train_cv_knn`: a nearest-neighbour baseline trained and evaluated in folds within the training-domain data, used as an empirical signal proxy (not exact mutual information or the Bayes accuracy).
- `train_probe_accuracy`: for **each target architecture and intervention**, a two-fold out-of-fold diagnostic computed exclusively from the training-domain records. Final test labels are never used to compute this score. The probe is an *allowable small experiment on the previously unseen architecture*, not zero-shot prediction of its properties.

The candidate forecast law has the empirical form

```
accuracy_hat_new = clip_0_1( probe_accuracy_new
                               + lambda * ridge(meta_features) )

ridge(meta_features) predicts (observed_accuracy - train_probe_accuracy)
```

Metadata includes log train size, log feature count, train-only kNN and architecture probes, train class entropy, prespecified architecture descriptors, known sensor/label corruption rates, and an unlabeled train-to-test covariate-shift statistic. The model is a **candidate predictive relation**, not an asserted invariant theorem.

The shrinkage `lambda` is chosen in the outer **training portion** using nested group-holdout meta-validation among candidate values `0, 0.1, 0.25, 0.5, 1`. Zero means the complex correction is rejected and the honest train-only probe is used instead.

### Three genuinely withheld validation regimes

1. `unseen_dataset`: all final-test observations from one entire dataset are excluded from meta fitting, across every architecture and seed.
2. `unseen_architecture`: all final-test observations from one architecture are excluded from meta fitting, across every dataset and seed.
3. `unseen_both`: all rows from either one target dataset **or** one target architecture are excluded from fitting, then predictions are evaluated where they intersect.

Model selection uses only the permitted outer training rows. The two baselines are (a) constant training-set mean accuracy and (b) direct training-only probe accuracy. Reporting only improvements against the constant baseline would be misleading.

**Critical qualification:** Because a training-only probe of the new architecture is permitted, regimes 2 and 3 test *architecture extrapolation with a calibration experiment*, not prediction from the architecture description alone. A strictly zero-shot theory remains unproved.

## Separate modality and model tracks

`--text-study`: optional 20 Newsgroups official train/test split, textual TF-IDF with logistic, naive Bayes and linear SVM over seeded train perturbations. Internet required on first use. Text results are reported separately because the tabular/image candidate is not calibrated across text. This experiment does not produce a site-level domain holdout.

`--local-benchmark file.jsonl --model installed-ollama-model`: separate direct/verify prompt paired benchmark on a **pretrained local** model and real question/answer examples. Optional GSM8K download helper produces number-answer JSONL from the public test split. No samples or results from this path are merged into V1 synthetic trials or V2 numeric forecasting.

The local model path tests *prompting*, not weight updates or genuine process-supervised training. The distinction matters when interpreting OpenAI's process-supervision paper.

## Replication and falsification checks

- Inspect `observations.csv` for every dataset/seed/model/intervention/domain; `law_predictions.csv` for every prediction including those that failed.
- Inspect `forecast_groups.json` for inner-selected correction weights, including zero weights, and holdout provenance.
- Check `excluded_runs.json` for samples that could not be analysed. Failures are never silently converted into scores.
- Compare both candidate error and probe-only error macro-averaged by **held-out dataset or architecture**, not only pooled over repeated seeds.
- Use >=20 seeds as the minimum sensitivity exercise; acquire many more **independent sources** for externally valid inference.
- For causal interpretations, use true interventions with independent outcomes or a design that identifies the intervention effect. OOD accuracy differences can reflect label prevalence changes and feature confounding.
- Do not tune on the final holdout. If the law fails, freeze a new version and test its revision on *new, uninspected* heldout families.

## Core research methods being adapted, with explicit differences

- Burns et al. (OpenAI), *Weak-to-Strong Generalization* (2023): paired weak/strong learners, negative appendix findings and distinct supervisory signals. V2 uses the comparison principle but does not claim to replicate pretrained GPT-4-family experiments.
- Lightman et al. (OpenAI), *Let's Verify Step by Step* (2023): process vs outcome verification. V2's local benchmark uses an optional verification *prompt*; it does **not** substitute prompts for a learned process reward model.
- Hoffmann et al. (DeepMind), *Training Compute-Optimal Large Language Models* (2022): independent scaling axes for data/compute. V2 records size/architecture sensitivity, not a fitted frontier LLM compute-optimal scaling exponent.
- Koh et al., *WILDS* (2021): focus on distribution shifts with metadata-defined domains. The built-in feature-median split is an inexpensive analog only; custom site/time CSV is closer to a natural domain partition.
- Kalai et al. (OpenAI), *Why Language Models Hallucinate* (2025): distinguish calibrated abstention from guessing. V2 includes brier score and the separate pretrained-model answer-format/error audit; no universal hallucination-rate theory is established.

## Publication standard for a V3 claim

Before calling this a law, require an **uncertainty-bounded** gain over *probe only*, not merely over a constant; a closed-form or reproducible predictor independent of test labels; robust performance on datasets never seen during development; real site/time/writer shifts; multiple modalities and genuinely different learning schemes; and independent labs reproducing the same magnitudes. Predeclare stopping, acceptable effects, access protocol and dataset licenses before commencing confirmation.
