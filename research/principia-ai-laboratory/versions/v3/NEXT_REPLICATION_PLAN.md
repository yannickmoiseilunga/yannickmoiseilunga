# Next independent confirmation — without retuning the V3 law

## Why the initial test is not conclusive

V3 was fit on four development datasets and evaluated on three additional real source families (four for a separate unseen-architecture comparison). The new families and architectures were not used for fitting coefficients, but only three or four *independent source families* underlie the confidence intervals. Repeating 20 seeds reduces within-source sampling noise but does not multiply the number of independent worlds.

## Planned decision rule

- Freeze V3 coefficients, source data, code hash and protocol **before downloading** any additional source labels.
- Use non-overlapping projects, institutions, acquisition regimes and/or data-generation processes where possible. File source hashes, versions, data collection notes and allowed reuse licenses.
- Primary endpoint: dataset-macro mean gain in MAE relative to *the same target architecture's training-only probe*; predefined smallest useful gain **0.01 absolute accuracy MAE**.
- Report 95% dataset-cluster confidence interval for gain, independent source count, negative family results, missing runs and power assumptions; a CI with lower limit >0 *and* average gain ≥0.01 would qualify only as empirical support conditional on included source families.
- Include the simple V2 residual Ridge reference with its weight fitted solely from development sources. Do not select based on new source outcomes.
- Repeat across image, text, tabular, time-series, audio (when properly labelled) and several explicit feedback schemes; do not combine incomparable metrics without preregistered normalisation.
- Clearly separate predictions with a two-fold training-only probe from **zero-shot predictions without touching a new architecture's fit**; the latter is more ambitious.
- For domain shift, collect and hold out genuinely independent hospitals/sites/years/writers where metadata exists; feature-median shifts are only a weak proxy.
- Use uncertainty sets or intervals for any unknown conditional shift. Unlabeled target covariates alone cannot identify target labels.

## Illustrative prospective number of source families

Assuming independent source-family gains have standard deviation 0.03 absolute MAE, target effect 0.01, two-sided alpha 0.05, and 80% power, the standard normal approximation gives:

    n_source ≈ ceil([ (z_0.975 + z_0.80) * 0.03 / 0.01 ]²) = 71 independent sources.

At SD 0.02 this becomes 32 sources, at SD 0.05 it becomes 197. These are illustrative assumptions and not a claim of power from the existing 3–4 datasets. Correlation and distinct modality strata may require more.

## Ready for a laptop

Version 3's `--transport-study` command remains fully offline for its included survey collections. Version 2's `--real-study` CLI also supports OpenML datasets and user-labelled CSVs, but a future V3 release should put a *new frozen-source registry* between external data import and evaluation, to prevent unintentional retuning against test labels.

A rented GPU is not required for this statistical test; data diversity and independent-source design are the constraint. When expanding to actual pre-trained LLMs or vision Transformers, freeze architecture selection and evaluation tasks, then rent time-bounded compute after profiling a small CPU/local batch.
