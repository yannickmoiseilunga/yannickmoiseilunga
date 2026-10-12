# Development ablations — deliberately negative findings

All numbers below come from the **same four public datasets and same 20 master-seed replications**, which were used during programme construction and predictor tuning. These are **not prospective confirmatory results**. Their purpose is to make the pathway from an overfitted descriptive rule to a more constrained forecast auditable.

| Design explored during development | Leave-dataset-out MAE | Leave-architecture-out MAE | Dataset-plus-architecture-out MAE |
|---|---:|---:|---:|
| First metadata-only Ridge predictor, no new-architecture diagnostic | 0.1122 | **0.2894** | **0.2859** |
| Probe-plus-unshrunk Ridge correction | 0.0895 | 0.2185 | 0.2105 |
| Probe-plus-nested-validated correction (release candidate) | 0.0936 | 0.1231 | 0.1124 |
| Probe only, with no meta-model correction | 0.1039 | **0.1039** | **0.1039** |

The candidate law was improved during development, so the final comparison must be performed on genuinely untouched data. The *probe-only* baseline is superior under the architecture and combined holdout in these observations. For future trials, the acceptable effect must be fixed in advance, and gains must clear uncertainty over independent source groups. There are no universal architecture-generalisation findings here.

Source for the release-candidate row: `reports/real_v2_20261012T111926Z_s42` in this package. Per-experiment outputs and the source-code/experiment protocol are provided.
