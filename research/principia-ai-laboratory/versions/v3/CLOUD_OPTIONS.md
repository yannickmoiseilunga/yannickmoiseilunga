# Computing options for expanded experiments

**Do not rent GPU compute for the bundled four-dataset V2 experiment.** It uses scikit-learn CPU estimators, and a GPU will not automatically speed it up. First try your laptop, then enlarge the number of independent datasets and group sources before buying more seeds or FLOPs.

## If the optional local LLM or deep-vision experiment becomes too large

| Option | What makes it useful | What to check before paying |
|---|---|---|
| Google Colab (free) | Small notebooks with limited, non-guaranteed GPU/TPU access | Free resources and session limits fluctuate. A laptop-run browser server is not the right free-Colab workflow. |
| Google Colab paid / Pay As You Go | More compute and managed notebooks | Compute units, regional price, timeouts and available accelerator before purchase |
| Vast.ai | Competitive marketplace offers, often low-cost used NVIDIA GPUs | Current offer, storage, egress, uptime/interruptibility and host reputation |
| Runpod | GPU Pods and managed infrastructure | Compare Community/Secure pricing, attached storage, idle time and data transfer |

Official pricing and limits (check live prices before renting):
- https://research.google.com/colaboratory/faq.html
- https://vast.ai/pricing
- https://www.runpod.io/pricing

Example cost estimation: `total_cost = GPU_hourly_rate * billable_hours + disk/storage + data-transfer + taxes/fees`. A hypothetical £0.30/hour instance for 5 hours costs £1.50 **before** additional charges; it is not a current quote.

## Moving an evidence run to cloud

Use an ordinary Python venv and the same command:

```
python -m pip install -r requirements-research.txt
python main.py --real-study --seeds 20 --datasets breast_cancer,wine,iris,digits
```

Save the `reports/real_v2_*.zip` artifact somewhere durable before shutting down an ephemeral instance. Do not expose the local workbench HTTP server directly to the public internet; it was designed to bind to localhost, not as a secured multi-user server.

## Better research spending order

1. More truly independent task families and observed site/time domains.
2. Clean labels, data provenance, and avoidance of train/test leakage.
3. Evaluation replicates of previously untouched domains, with uncertainty estimates.
4. Only then compute-intensive models and rented GPU resources.

A large TPU cannot solve confounding or data leakage. A failure against the probe baseline on cheap CPUs is often more informative than increasing FLOPs.
