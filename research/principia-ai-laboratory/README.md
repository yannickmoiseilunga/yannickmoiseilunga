# Principia AI Laboratory: An experimental search for transferable laws of machine learning

**Research status: exploratory; no universal law proven.** Three evolving versions inspired by Newton's method of definitions, propositions, experiments, counterexamples and revision. These are **not** Newton's actual laws of intelligence.

## Read this first (2 minutes)

Can a mathematical relationship forecast how a trained learner will perform when its data, architecture, or both are new? We tested the claim, found failures, and changed the candidate law instead of removing adverse outcomes.

| Version | Investigation | Central finding |
|---|---|---|
| [V1 – Synthetic Mechanisms](versions/v1/README.md) | 12 controlled hypotheses on information, composition, correction and feedback | 11 were consistent on toy worlds, 1 inconclusive; initial forecasts sometimes violated Bayes accuracy ceilings |
| [V2 – Real-Data Replication](versions/v2/README.md) | 20 seeds, 4 publicly distributed datasets, source/architecture holdouts | Improved over probe on held-out dataset but failed on held-out architectures |
| [V3 – Information–Transport Law](versions/v3/README.md) | Conditional error-log-odds model, new survey sources and architectures | Lower average error on some held-outs, but **none passed confirmation threshold** |

### Headline predictive results
**Mean absolute error (MAE); lower is better.** V2 and V3 are different studies, **not directly matched benchmark scores**.

| Version | Evaluation | Candidate MAE | Probe-only MAE | Result |
|---|---|---:|---:|---|
| V2 | New dataset | 0.0936 | 0.1039 | Development-stage improvement |
| V2 | New architecture | 0.1231 | **0.1039** | Negative finding |
| V2 | Both unseen | 0.1124 | **0.1039** | Negative finding |
| V3 | New dataset | **0.0573** | 0.0669 | Mean gain; not confirmed |
| V3 | New architecture | **0.0693** | 0.0711 | Mean gain; not confirmed |
| V3 | Both unseen | **0.0576** | 0.0613 | Mean gain; not confirmed |

V3 confirmation demanded >=0.010 absolute MAE gain **and** a positive lower bound of the source-cluster confidence interval. All three tests failed this gate.

### Interviewer navigation
- [Plain-English and technical interview briefing](docs/INTERVIEW_GUIDE.md)
- [Reproducible research findings and limitations](docs/EVIDENCE_AND_FINDINGS.md)
- [Reproducibility and source-code publication status](docs/REPRODUCE.md)
- [Mathematical derivation](versions/v3/V3_MATHEMATICAL_DERIVATION.md)
- [Future independent replication protocol](versions/v3/NEXT_REPLICATION_PLAN.md)
- [Published raw V2 development records (CSV)](versions/v3/frozen_development_v2.csv) and [evidence inventory](docs/RAW_EVIDENCE_README.md)
- [V1 experimental report](versions/v1/reports/20261012T103053Z_standard_s42/REPORT.md)
- [V2 empirical report](versions/v2/reports/real_v2_20261012T111926Z_s42/REPORT.md)
- [V3 empirical report](versions/v3/reports/transport_v3_20261012T121322Z/REPORT.md)

### Publication scope
This initial GitHub publication contains source methodology, protocol descriptions, result summaries, and the frozen V2 development observations (1,920 records). **The full executable source trees and raw prediction CSV/JSON evidence are staged in a separate local publication bundle and require the repository sync step**; no such files should be assumed to exist on GitHub until uploaded and verified. Tests in that package have passed (11 V1, 20 V2, 30 V3), but that is not third-party scientific validation.

The work was developed iteratively with AI assistance. It does not claim peer review, architecture-independent emergence, consciousness or a universal intelligence theorem.