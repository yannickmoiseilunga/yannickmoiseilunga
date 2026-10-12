# Principia — Mathematical derivation and necessary restrictions

**Newtonian inspiration**: an established disposition persists until acted on by altered observations or corrections. In the statistical analogue, a trained model's measured source-domain performance is an inertial reference, and shifts in sensing and data distribution may change performance. This analogy does not imply error obeys mechanics, conservation of momentum, or universal forces.

## Proposition I — the log-odds transport relation

Let the training-only calibration probe yield accuracy p. For target environment Q, assume that the *ratio of error odds*, relative to the calibration environment, is positive and takes an exponential-family approximation:

    odds(error_Q)/odds(error_source) = exp(lambda * beta · phi).

Because odds(error)=R/(1-R), taking logarithms yields

    logit(R_Q) = logit(1-p) + lambda beta·phi;
    A_Q=1-sigmoid(logit(1-p)+lambda beta·phi).

Here `phi` contains unlabeled feature displacement, its square, shift × |p−0.5|, cross-learner ability gap, calibration Brier, known label/sensor corruption, and logarithmic sample-efficiency. The law differs materially from V2's additive accuracy prediction because it is additive in *error log-odds*, hence multiplicative in the odds ratio, with a bounded sigmoid output. It remains an empirical parametric assumption.

Fit `beta` with ridge regression (alpha 50) on Version 2 observations; source targets are logit(observed error) − logit(probe error), clipped to [0.005,0.995]. Shrink its contribution by fixed lambda=.35. No V3 held-out test labels enter parameter estimation or shrinkage selection. All feature preprocessing is fitted only to training sources.

## Proposition II — finite-sample stability

Error odds may be extremely large for scores near zero and extremely small near unity. Numerical clipping prevents divergent logarithms, but introduces bias for truly perfect systems. A fitted coefficient is *not* a causal parameter. A bounded output is desirable but does not give an information-theoretic ceiling.

## Proposition III — impossibility of an unconditional law

Let training distribution P(X,Y) and unseen input distribution Q_X be exactly the same in worlds W1 and W2. Let W1 assign test labels Y=f(X), and W2 assign test labels Y=1−f(X), with all other observable conditions unchanged. For any fixed learner h using only training labels and test inputs, its target accuracies satisfy A1+A2=1. Any common point forecast a must have max(|a−A1|,|a−A2|) ≥ |A1−A2|/2. For near-perfect h, this minimax forecasting error approaches 1/2. No amount of training-history observation or unlabeled target information resolves this without restricting conditional shift or acquiring independent target labels. This is a constructive identification limit, not merely a negative machine-learning benchmark.

## Conditional guarantee as a *separate* theorem

For 0-1 loss, if both full joint distributions P(X,Y) and Q(X,Y) are defined on a common measurable sample space, then:

    |R_Q(h) − R_P(h)| ≤ TV(P_{XY}, Q_{XY}).

This follows immediately by applying the definition of total variation to the error event {(x,y):h(x)≠y}. The bound is universal and exact, but full joint total variation cannot generally be determined from unlabeled target X. Any usable guarantee must assume/bound changes in Q(Y|X), source support, or label observability. The empirical V3 shift_proxy is NOT a substitute for that joint-TV term.

## Statistical testing and uncertainty

Macro-average MAE over independent dataset families; don't treat seeds as independent data sources. Three transfer tests are predefined. The decision threshold is gain ≥ .01 absolute MAE with cluster-level t 95% lower confidence bound above zero; with 3–4 source clusters tests have very low power. Source-fit in-sample residual quantiles are reported to display width, NOT as conformal or distribution-free OOD guarantees. A formal conformal guarantee would demand exchangeable calibration examples from the target distribution or additional correct weighted-shift assumptions.

## Sources

- Newton, Principia (Motte, 1729): https://en.wikisource.org/wiki/The_Mathematical_Principles_of_Natural_Philosophy_%281729%29
- Cover and Thomas, Elements of Information Theory (data processing and information bounds): https://onlinelibrary.wiley.com/doi/book/10.1002/047174882X
- Ben-David et al., a theory of learning from different domains: https://arxiv.org/abs/0902.3430
- Arjovsky et al., Invariant Risk Minimization: https://arxiv.org/abs/1907.02893
- Gulrajani and Lopez-Paz, DomainBed: https://arxiv.org/abs/2007.01434
- OpenAI, neural scaling laws: https://openai.com/index/scaling-laws-for-neural-language-models/
- PAC-Bayes and domain adaptation: https://doi.org/10.1016/j.neucom.2019.10.105
- UCI datasets optionally supported from the V2 research suite: https://archive.ics.uci.edu/
