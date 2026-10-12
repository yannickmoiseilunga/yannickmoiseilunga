# Papers and methodological lineage

References are listed for transparency. The programme implements **small-scale analogues** of certain experimental patterns; no claim of reproducing the published numerical findings, appendices, pretrained models or original code.

1. **Isaac Newton**, *Philosophiæ Naturalis Principia Mathematica* (1687; Andrew Motte English translation, 1729). Historical structure of definitions, laws, demonstrations and scholia. https://en.wikisource.org/wiki/The_Mathematical_Principles_of_Natural_Philosophy_(1729)
2. **Kalai, Nachum, Vempala & Zhang (OpenAI, 2025)**, *Why Language Models Hallucinate*. https://arxiv.org/abs/2509.04664 — Statistical unidentifiability and the impact of rewarding guessing over abstention. Adapted here as hidden observations, confidence calibration and selective prediction.
3. **Lightman et al. (OpenAI, 2023)**, *Let's Verify Step by Step*. https://arxiv.org/abs/2305.20050 and https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/ — Step-level versus final-answer verifiers, best-of-N selection. Here arithmetic trails have deterministic ground truth and deliberately noisy verification signals. The verifier strengths need not be equivalent; they are recorded as design choices.
4. **Burns et al. (OpenAI, 2023)**, *Weak-to-Strong Generalization*. https://arxiv.org/abs/2312.09390; source https://github.com/openai/weak-to-strong — Teacher vs stronger student and gold-label controls. Toy linear teachers and interaction students in this programme are a **negative-control analogue**, not a finetuning replication.
5. **Hoffmann et al. (DeepMind, 2022)**, *Training Compute-Optimal Large Language Models* (Chinchilla). https://arxiv.org/abs/2203.15556 — Multi-axis architecture/data sweeps and attention to compute budget, scaling-law fitting methods. Toy data and parameter sweeps here must not be extrapolated to LLM scale.
6. **Koh et al. (2021)**, *WILDS: A Benchmark of in-the-Wild Distribution Shifts*. https://proceedings.mlr.press/v139/koh21a.html — Environment-heldout evaluation; our controlled spurious-world training and shifted test condition.
7. **Starace et al. (OpenAI, 2025)**, *PaperBench: Evaluating AI's Ability to Replicate AI Research*. https://proceedings.mlr.press/v267/starace25a.html — Explicit decomposed checklists and grading, adapted as preregistered hypotheses and machine-readable observations.
8. **OpenAI (2024)**, *Learning to Reason with LLMs*. https://openai.com/index/learning-to-reason-with-llms/ — Search and test-time candidate evaluation, motivating fixed-budget verification curves.
9. **Wang et al. (ACL, 2025)**, *SConU: Selective Conformal Uncertainty in Large Language Models*. https://aclanthology.org/2025.acl-long.934/ — The importance of uncertainty evaluation, exchangeability limits and distribution shift. Our risk-coverage test **is not conformal prediction** and makes no formal conformal coverage guarantees.
10. **Cover & Thomas**, *Elements of Information Theory*, Ch. 2 — data-processing inequality and mutual information. https://sgfin.github.io/files/notes/Cover_and_Thomas_ch2_entropy.pdf

Additional treatment of appendix-level design ideas is provided in `RESEARCH_METHODS.md`. Do not attribute the experimental corollaries to Newton or the listed authors.

## Additional sources checked for Version 2 (October 2026)

- OpenAI — *Weak-to-Strong Generalization: Eliciting Strong Capabilities With Weak Supervision*, https://arxiv.org/abs/2312.09390 and official code https://github.com/openai/weak-to-strong. The supplementary appendices describe negative and additional weak-supervision experiments.
- OpenAI — *Let's Verify Step by Step*, https://arxiv.org/abs/2305.20050 and PRM800K https://github.com/openai/prm800k.
- OpenAI — *Why Language Models Hallucinate*, https://arxiv.org/abs/2509.04664.
- OpenML scikit-learn integration https://docs.openml.org/ecosystem/Scikit-learn/ and `fetch_openml` reference https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_openml.html.
- scikit-learn public datasets https://scikit-learn.org/stable/api/sklearn.datasets.html; digits provenance https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html.
- WILDS real distribution-shift research https://wilds.stanford.edu/get_started/ (large datasets intentionally NOT automatically downloaded here).
- Hugging Face dataset loading and streaming https://huggingface.co/docs/datasets/en/loading.
- Ollama local `/api/generate` specification https://github.com/ollama/ollama/blob/main/docs/api.md.
- Google Colab official limits and paid tiers https://research.google.com/colaboratory/faq.html.
- Official GPU pricing https://vast.ai/pricing and https://www.runpod.io/pricing.

The software does not claim to reproduce frontier-scale experiments, numerical paper findings, the original authors' complete datasets, or their trained weights. All download access and usage remain subject to upstream licenses and rules.
