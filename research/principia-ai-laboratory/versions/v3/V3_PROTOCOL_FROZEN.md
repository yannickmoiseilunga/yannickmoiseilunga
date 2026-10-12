# CONDITIONAL INFORMATION-TRANSPORT LAW: PROTOCOL FREEZE

Revision version: 3.0.0, code written before accessing target evaluations from ANES96, RANDHIE and Fair datasets.

## Mathematical candidate

Let p denote the target architecture's two-fold out-of-fit training-only accuracy, q its data-only KNN probe, b its training-only Brier score, n its source-sample size, d its number of features, f and s known correction/sensor fidelity, and Delta_X an unsupervised feature-shift statistic. Define phi=(1,Delta_X,Delta_X^2,Delta_X|p-.5|,q-p,b,1-f,1-s,log(1+n)/(1+log(1+d))).

**Information-Transport Log-Odds Law:**

    logit[1 - A_Q] = logit[1 - p] + 0.35 * beta.T @ phi

beta = Ridge(alpha=50) fit on logit(error_observed)-logit(error_training_probe) exclusively in pre-existing Version 2 source worlds. Accuracy is 1-sigmoid(logit_error); clip source accuracy and probe in [0.005,0.995]. Ridge preprocessing is StandardScaler fitted on source only.

Interpretation: an inertial training-only error state, corrected by statistical 'forces' of shift, correction fidelity, and learnability. The logistic form prevents predictions outside [0,1]. Novelty lies in the proposed composition and external falsification test, not in claiming the logit, Ridge, or Newtonian metaphor are newly discovered mathematics.

**Crucial theorem**: Without assuming bounds on changes in P(Y|X), no single point law for unseen-world accuracy can be universally correct. Two worlds can share identical P_train(X,Y), P_test(X), architecture and probe but reverse P_test(Y|X). This prevents universal identification, independent of mathematical elaboration.

## Primary prospective comparison (exploratory at present)

- Primary: V3 mean absolute error minus train-only probe, macro-averaged at independent dataset level. Require V3 improvement >=0.01 and a positive lower limit of dataset-level 95% CI for signal of support.
- Secondary: V3 vs reproduced V2 nested Ridge correction.
- 20 deterministic seeds 42+1009*k; alternative models GaussianNB and distance-weighted kNN are not included among V2 development models.
- Frozen external sources: ANES96 (vote), RANDHIE (physician visit vs none), Fair (binary affairs vs none). Domains are population median, health-plan idp, and duration median respectively. Medical/survey datasets are not interpreted clinically; all observations are public.
- Evaluation: new datasets with old linear/prior architectures; new architectures on old datasets; new architectures on new datasets. No post-hoc deletion of negative regimes.
- Three interventions: clean, 20% training-label inversion, 40% independent feature masking.
- Source calibration: Version 2 1,920 rows with SHA-256 stored in reports. These were already inspected. Source in-sample error percentile bands are not valid coverage guarantees.
- An additional exact constructive concept-shift impossibility witness is mandatory.
- The frozen trial uses local statsmodels bundled data because independent UCI downloads are not accessible in this environment. The programme can still access optional OpenML via V2 commands when run locally online.

**Limits**: prospective in model-fitting order only; no third-party timestamped preregistration. Natural domain shift, unseen deep architectures and text language-model transfer remain separate scientific challenges; do not overstate.
