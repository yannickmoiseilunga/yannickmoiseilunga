# Principia AI — Protocol and Experiment Atlas

## 0. Proposed universal corollary: its measurable form

Let `W` be the latent world state, `A` the observations accessible to an engine, `D` the disposition acquired in training, `C` the correction signal, and `J` the resulting judgement.

> Artificial judgement is determined by the engine's constitution and acquired disposition jointly with currently accessible observations; correction may alter future dispositions; and reliable distinction requires distinguishable evidence or prior grounds.

For a closed inference chain `W → (D,A) → J`, the data-processing inequality yields `I(W;J) ≤ I(W;D,A)`. This statement is **provable only under the specified information-flow assumption**. It does not prohibit new information gained from a tool call, an experiment, independent randomness correlated with the world, or an intervention affecting subsequent observations. In a fair hidden-bit task, the exact Bayes bound is `0.5`, and `I(W;A)=0` bits.

Three operational quantities:

1. **Distinguishability**: `I(W;A)=H(W)-H(W|A)` and Bayes accuracy `Σ_a max_w P(a,w)` from enumerated exact known synthetic distributions. The information quantity is descriptive and not an accuracy bound by itself without specifying a source distribution and decoding task.
2. **Transformation**: measured ability of a given representation to learn an XOR relationship from examples; compare held-out accuracy versus the Bayes ceiling using `Prior`, `Logistic`, `Interaction Logistic`, `TinyMLP`; hold dataset constant as architecture changes.
3. **Correction**: accuracy, Brier loss, log-loss and calibration under clean, inverted and noisy correction targets; measured in **true world labels**, not in the reward label that trained the system.

## 1. General experimental design

Synthetic samples are generated using separate seeded streams. Training uses labels available for correction; evaluation always uses independent ground truth withheld from the learner. The paired-seed protocol reduces variability when comparing interventions. Test domains are generated independently from train domains. No test labels are used in learner optimisation. Small-scale study; run `--preset extended` for 20 independent seed replications.

For each trial, store `experiment, model, seed, domain, n_train, params, ops_proxy, train_seconds, n_test, accuracy, brier, log_loss, ece, selective_risk_80`, and when possible `bayes_accuracy, mutual_information_bits`. The `ops_proxy` is a deterministic algorithmic operation counter, **not FLOPs**. The test-set prediction archive is deterministically sampled to 200 rows per cell for memory control; aggregate metrics use all observations.

## 2. Falsifiability register

| ID | Question and control | Registered comparison | Limitations |
|---|---|---|---|
| H01 | No informative impression: can the engine reliably distinguish an independent hidden bit? | Linear accuracy differs from 0.5 by no more than 0.05, seed bootstrap | Approximate statistical equivalence; only exact mathematical ceiling is a theorem |
| H02 | Are additional independent observations useful? | 3-sensor linear accuracy minus one weak sensor accuracy > 0.03 | Particular sensor reliabilities chosen a priori |
| H03 | Can architectural composition represent XOR? | Interaction model minus linear on large parity set > 0.10 | Does not demonstrate general reasoning emergence |
| H04 | What is the effect of changed conditions? | ID minus shifted accuracy > 0.10 on spurious world | Shift construction is deliberately large |
| H05 | Does improving the wrong objective reduce true accuracy? | True-label training minus inverted-label training > 0.25 | Exact inversion is an extreme toy construction |
| H06 | Can corrupted supervision be detected when accuracy stays unchanged? | Brier loss(noisy correction) minus Brier loss(clean) > 0.012 | Calibration depends on architecture and noise |
| H07 | Does an additional instrument help? | Adaptive-tool accuracy minus unaided accuracy > 0.025 | Sensor reliabilities and cost model explicitly supplied |
| H08 | Does an external reference distinguish arbitrary unseen identities? | Registry lookup accuracy minus unassisted > 0.20 | Registry contains truth; access to it is a new information channel |
| H09 | Can deliberation with a verifier outperform a first answer? | Process best-of-16 minus first-of-1 > 0.05 | Toy arithmetic; supervision information differs from outcome method |
| H10 | Can weak-to-strong supervision help on new structure? | Interaction student with weak labels minus weak teacher > 0 | Open exploratory, no promised success |
| H11 | Can selective abstention improve error rate? | Overall error minus top-80%-confidence error > 0.015 | Does not guarantee correct uncertainty outside ID distribution |
| H12 | Does post-action feedback improve control? | Closed-loop success minus open-loop > 0.04 | Higher fidelity sensor used post action; sensor advantage partly responsible |

Effect confidence intervals are bootstrapped across random seeds. `consistent (exploratory)` means the entire percentile interval clears the registered threshold (or lies within the tolerance for H01). `contradicted here` means measured confidence interval is across the negative direction. Otherwise `inconclusive`. These are **descriptive** intervals with no multiplicity adjustment or guarantee of nominal hypothesis test error rate. Stronger claims need independent domains, large preregistered repetitions, and uncertainty accounting for dataset selection.

## 3. Synthetic world mechanisms

**Blind**: `Y ~ Bernoulli(0.5)`, each observed bit independent of `Y`. Enumerating `2×2³` joint possibilities gives an exact ceiling `0.5` and `I(Y;X)=0`.

**Sensors**: Three conditionally independent noisy indicators, accuracies `(0.78, 0.72, 0.67)`, each built by flipping `Y` with its respective probability. Comparisons mask either one or multiple sensor coordinates. Bayesian joint probabilities are enumerated, not approximated by Monte Carlo.

**Parity**: independent bits `A,B`, output `Y = A XOR B`, plus independent nuisance bit. Linear logit is a deliberately insufficient representation of XOR; pairwise products make it linearly separable in the enlarged representation. Note that `I(Y;(A,B))=1` bit even though each individual bit alone conveys no information.

**Spurious**: strong stable observation with `P(X0=Y)=0.82`; train shortcut `P(X1=Y)=0.97`, test shortcut `P(X1=Y)=0.12`. OOD is evaluated with the SAME fitted learner and without test-time corrections.

**Alignment**: informative channel with `P(X0=Y)=0.93`. Under clean correction use `Y`; inverted correction use `1-Y`; noisy correction independently flips training targets with probability 0.26. Ground-truth evaluation always checks `Y`.

**Math verification**: Generate `((a+b)*c)-d`; sample candidate steps with per-step mistakes. The process verifier checks local arithmetic consistency (with 9% label noise). Outcome verification checks final correctness (with 23% label noise). Equal performance must not be presumed because the two verifiers have unequal access to information and unequal error rates. Compare best-of-1/4/16 at fixed item seeds. This follows the *design contrast* of OpenAI's process versus outcome supervision, not its exact neural reward model or PRM800K dataset.

**Weak teacher transfer**: a linear learner is fitted to XOR, generating pseudo-labels for an interaction-capable student, alongside the true-label trained gold control. If the teacher excludes the critical relation, the pupil may have no way to recover it. The experimental failure is informative, and is kept in results. Inspired by the weak/strong supervised comparisons and ablations of Burns et al.; no external GPT models used.

**Active sensing**: two weak independent Bernoulli sensors. The policy queries a third highly informative instrument either never, always, or only when the first two disagree. The decision uses additive log-likelihood ratios based on **known** sensor reliabilities. This quantifies the value of acquiring additional information, including an action cost measured as query fraction.

**Memory**: one random independent truth bit assigned to each registry identifier. The test contains identifiers never available through initial observations. An external registry query reveals exact truth. No construction without that observation can exceed its prior-information bound reliably.

**Control**: hidden binary state, imperfect initial measurement and imperfect flip action; compare a one-shot command with two extra high-fidelity (97%) post-action measurements and corrective actions. This specifically illustrates the difference between generating an answer and intervening in a dynamical world. Measurement quality is a confound and explicitly part of the treatment.

**Self-training**: a linear sensor engine repeatedly replaces ground-truth supervision with its own binary predictions, records fresh held-out calibration and correctness without ever feeding those test labels back. Changes in confidence are not automatically improvements in true agreement.

**Apparent equivalence**: train two distinct constitutions on the same sensor world and compute the agreement fraction on heldout judgements. Equal outward judgements cannot identify unique internal mechanism.

## 4. Prediction of unseen outcomes: more than a relabelling

The `principia/prediction.py` candidate does not use held-out accuracy as a feature. It fits a small regularised linear model to operational design features (`Bayes ceiling`, mutual information, data count, parameter count, architecture indicators, parity structure, corrupted/inverted correction, and domain shift). For each experiment family it fits on every *other* family and predicts accuracy on the fully withheld family. It reports every prediction, absolute error, a training-mean accuracy baseline and any **predictions exceeding the known Bayes ceiling**.

This is a meaningful, prospective-style out-of-condition prediction challenge but **not** a new universal law. The feature design is heuristic and contains detailed knowledge of these constructed worlds; leave-one-family-out does not imply transfer to genuine unmodelled real worlds. It may fail substantially, and the programme does not hide failed forecasts. A validated successor would need to predict entirely new generators, datasets, architectures and tests selected before the model was fitted.

## 5. External tests and levels of evidential strength

- **Level A: mathematical theorem**. Exact data-processing inequality or Bayes-optimal ceiling under well-defined information channels.
- **Level B: controlled simulation**. Randomised causal synthetic tests; supports an instance of a hypothesis with numerical variability.
- **Level C: independent observed world**. User-provided CSV binary classification; held-out target and optional domain separation. Does not reveal exact Bayes ceiling or causal structure.
- **Level D: local LLM behavioural evaluation**. Optional local Ollama arithmetic, exact answer grading, reproducible prompts and raw output. Narrow capability coverage; no internals or training dataset visibility.
- **Level E: cross-institutional confirmation** (not supplied). External labs reproduce multiple architectures, environments and feedback types with preregistered conditions and independent audits.

All five levels must be kept separate when discussing whether a **general law** has been established.

## 6. Implementation choices and cited methodological appendices

- **OpenAI / Kalai et al. (2025), *Why Language Models Hallucinate***: the paper's statistical framing motivates an information-free world and scoring uncertainty instead of rewarding unjustified guessing. The toy abstention score checks high-confidence subsets, not open-ended truthfulness.
- **OpenAI / Lightman et al. (2023), *Let's Verify Step by Step***: compare candidate selection under noisy process versus outcome feedback; sample several candidate solutions; keep exact-answer holdout. It is not a PRM-trained replication. PRM800K labels and labelling appendices remain external, optional sources for future work.
- **OpenAI / Burns et al. (2023), *Weak-to-Strong Generalization***: retain controls trained against weak labels and controls trained against true labels. Its paper appendices examine experimental details, negative results, easy-to-hard regimes and additional settings; the toy experiment explicitly retains negative outcomes rather than assuming elicitation succeeds.
- **OpenAI / Starace et al. (2025), *PaperBench***: derive explicit granular criteria, record what was actually executed, and distinguish a reproduced result from a judged narrative. This lab uses local metric graders rather than LLM graders.
- **DeepMind / Hoffmann et al. (2022), Chinchilla**: vary sample counts, model capacity, and computational expenditure as independent factors. Our comparison does not estimate a universal LLM training-power law; toy classifiers are not language models and operation proxies are not FLOPs.
- **WILDS**: separate in-distribution and shifted conditions, keep trained disposition fixed while moving across environments, and report both performance regions rather than only the aggregate.
- **SConU / conformal literature**: evaluate confidence and risk-coverage, but make no conformal correctness claims absent an exchangeable calibration procedure.

## 7. Threats to validity

The evaluation follows a known synthetic generator. Its information geometry is discrete and conveniently enumerable. Independence and intervention assumptions are engineered, not discovered in nature. The named engines have tiny capacities. Performance differences may come from hyperparameters, selected datasets, or sample effects. Process supervision receives privileged knowledge of mathematical operation semantics; controls cannot be interpreted as equal-information comparisons. The closed-loop sensor is more reliable than its initial sensor, so the control experiment is a comparison of combined feedback and sensing quality. A model's forecast can fail even if data-processing theorems remain true. The presence or absence of any subjective experience or consciousness is outside the scope of these experiments.

**Primary success condition:** independently validated quantitative predictive relationships across unseen worlds and architectures, with limited error and pre-registered scope; **not** merely charts which agree with intuitive language.
