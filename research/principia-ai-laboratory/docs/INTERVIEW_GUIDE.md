# Interview guide: tell the scientific story in 2 minutes

## Plain-English account

> I built a sequence of experimental AI research systems inspired by Newton's idea of moving from definitions to falsifiable mathematical propositions. The research question was whether a model could predict how other learners perform on previously unseen datasets and architectures. The synthetic first version tested basic mechanisms; the second tested whether predictions transferred to real datasets and revealed architecture-transfer failures; the third introduced an odds-based predictive relationship and achieved smaller average errors in several transfer tests, but **failed the statistical confirmation criteria**. That honest negative result is important: it distinguishes an interesting empirical model from a universal law.

## Technical account

1. **Observable state:** architecture descriptors, training-only cross-validation probe, known correction/sensing interventions, unlabeled shift descriptors.
2. **Model:** Version 2 additive accuracy adjustment; Version 3 `logit(R_Q)=logit(R_probe)+λβᵀφ`, with a source-only fitted correction and bounded predicted accuracy.
3. **Evaluation:** dataset/architecture/double holdouts, seed repetition, dataset-family clustering, prospective effects and Holm corrections; no test labels admitted to predictor fitting.
4. **Baselines:** constant mean, probe-only, previous candidate; evaluate MAE, source-level uncertainty, failure subgroups and theory-limit violations.
5. **Failure mode:** unseen architecture advantage does not robustly transfer; small family count means broad intervals; unlabelled covariates cannot reveal arbitrary P(Y|X) changes.
6. **Decision:** claim an exploratory conditional predictor and an impossibility bound, not a discovered universal law.

## Likely senior researcher questions

**Q: What is novel?** A versioned, falsification-first experimental workbench joining classical scientific derivation, exact indistinguishability arguments, held-out transfer forecasting and negative-results reporting. The information bound and log-odds relation are **not** new mathematical theorems; the candidate combination and study design are experimental.

**Q: Why not simply use more training seeds?** Seeds reduce Monte Carlo variability, not between-domain epistemic uncertainty. The effective replication unit for universal transfer is the independent source family.

**Q: What prevents leakage?** Training-only probes, source-domain fitting, explicit target holdouts and retained provenance. But earlier benchmark development exposure means the bundle is exploratory; preregistration for future studies is not retroactive.

**Q: Why forecast rather than classify directly?** Forecasting learner performance before observing the new test labels is a more discriminating test of general theories of learning and transfer.

**Q: What is the weakest assumption?** That observable shift proxies and train-only probe performance sufficiently summarise how target correctness changes. Concept drift can falsify that assumption even when input distributions agree.

**Q: What is next?** Pre-register new independent source families, predict them before unsealing labels, calibrate interval coverage across sources, and compare with robust simpler baselines.

**Q: Did this use a frontier LLM?** Not in the reported tabular-transfer study. Optional Ollama adapter is a separate track; no actual language-model run is presented as completed evidence.
