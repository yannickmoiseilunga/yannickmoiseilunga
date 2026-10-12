# Reproduce or audit these experiments

The *complete* source and raw evidence ZIPs are prepared in the offline publication bundle. **This GitHub documentation-only stage does not yet contain those runnable sources**; after the publishing bundle is pushed, use its `versions/v1`, `versions/v2` and `versions/v3` folders.

For each version, run `python -m unittest discover -s tests` from that version's directory (Python >=3.10). Recorded regression-test counts: V1 11, V2 20, V3 30. For empirical V2 and V3 work, install `requirements-research.txt` (NumPy, SciPy, scikit-learn, pandas; V3 additionally statsmodels).

Example V2 study:
```bash
cd versions/v2
python -m pip install -r requirements-research.txt
python main.py --real-study --seeds 20
```
Consult each version's README and QUICK_START instructions for the exact V1/V3 CLI arguments and Windows launchers. Optional OpenML/Ollama studies require external data/model downloads and are separate from the included outcomes.

The source bundle contains full raw CSV/JSON predictions, experimental reports, source code, tests and a SHA-256 integrity manifest. Publication of all artefacts on GitHub is pending the authenticated sync and should be checked before claiming public reproducibility.