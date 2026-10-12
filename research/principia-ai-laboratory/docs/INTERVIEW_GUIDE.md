# Interview guide — explaining the research to different audiences

## Lay explanation
We asked whether you can predict how accurately a learning machine will do at a new task **before seeing its answers**. A simple mathematical rule should be tested on cases it did not learn from. V1 tested the principle with synthetic worlds; V2 tested more realistic data and found failure on unseen architectures; V3 changed the equation to work in error odds and produced modest average improvements. The gains did not survive the demanding confirmation rule, and those failures are retained.

## Two-minute technical explanation
We framed transfer forecasting as a conditional statistical prediction. The learner's architecture and *training-only* cross-validation accuracy form a probe, while descriptions of sensing, corrections and measured distributional shift form covariates. The V2 additive correction was brittle on architecture holdouts. V3 instead models **logit(target error) = logit(probe error) + λ·βᵀφ**, with trained coefficients carried from development sources to distinct holdouts. We compare mean absolute forecasting error against probe-only and V2 baselines, aggregate uncertainty across source families, and preserve negative results. No model can reliably predict arbitrary concept shift when input observations are identical but true labels differ.

## What an experienced interviewer might challenge

**Novelty?** A falsifiable, versioned research engineering programme; not discovery of the logistic function, information inequality or Newtonian dynamics in AI.

**Leakage?** Source-only coefficient fitting and training-only probes; target test labels excluded. Earlier observed V2 sources are explicitly development material.

**Why 20 seeds?** To reduce randomness within conditions. They are not 20 independent data-generating worlds; three or four held-out source families still give wide uncertainty.

**How was superiority decided?** A predefined minimum error improvement and source-level interval excluding zero. V3 did not pass.

**Where did it fail?** V2 failed unseen architectures and combined holdouts. V3 worsened certain source-specific predictions including ANES96, Digits and RANDHIE.

**Main unresolved limitation?** Unobserved changes in P(Y|X) cannot be deduced from unlabeled X alone. Training-probe accuracy is not zero-shot architecture prediction.

**Further work?** Freeze software and coefficients, gather many independent naturally separated source domains, perform a prospective power calculation at *domain level*, release all predictions, and seek independent replication.