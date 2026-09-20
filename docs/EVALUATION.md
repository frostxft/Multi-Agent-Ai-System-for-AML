# Evaluation and development review — 2026-09-14

The capstone uses transaction-node predictions to assemble connected investigation cases. It does not evaluate a supervised laundering-ring classifier. Neither scores nor benchmark labels establish criminal conduct.

## Fixed replication protocol

The original seed-17 report and deployed checkpoint remain unchanged. A separate study ran seeds **17, 29, 43**, each for 25 epochs with the original architecture, feature policy and optimizer. The protocol was saved before the study ran. No seed was selected as a winner; checkpoint selection uses validation AP and operating thresholds use validation F2. Both models receive the same splits, labeled targets, local features and scaling policy.

Training: time steps 1–29. Validation: 30–34. Evaluation: 35–49. Evaluation contains 16,670 labeled transactions, including 1,083 illicit labels. Unknown labels do not enter the supervised loss or metrics. Source fingerprint: `903ac5dfcabafb86638bbceddef49530bdad2743c6cfe71a7d1c78bf0da9f043`.

**Test-set qualification:** this temporal evaluation set was already observed in the initial project. This study reuses it for fixed replication, without tuning on it. It cannot honestly be called a newly untouched final set. No new architecture was promoted after observing these results. Further model development must use training/validation periods and reserve a genuinely new prospective or external evaluation population before making stronger generalization claims. Creating a subset of already inspected results would not repair that limitation.

## Measured results

Values are proportions. SD is sample standard deviation across three seeds (`ddof=1`), not a confidence interval or uncertainty across time periods.

| Model / seed | Precision | Recall | Average Precision (AP) |
|---|---:|---:|---:|
| GAT 17 | 0.159810 | 0.620499 | 0.210292 |
| GAT 29 | 0.144283 | 0.680517 | 0.248270 |
| GAT 43 | 0.159330 | 0.588181 | 0.243211 |
| **GAT mean ± SD** | **0.154474 ± 0.008829** | **0.629732 ± 0.046855** | **0.233925 ± 0.020622** |
| Logistic 17, 29, 43 (each) | 0.191597 | 0.804247 | 0.200893 |
| **Logistic mean ± SD** | **0.191597 ± 0.000000** | **0.804247 ± 0.000000** | **0.200893 ± 0.000000** |

Seed 17 exactly reproduced the original reported metrics. The logistic solver produces identical results for these seed settings on this fixed dataset; zero seed SD is not zero statistical uncertainty. The GAT has higher mean AP, while the baseline has higher precision and recall at the validation-selected thresholds. These are different operating points, not a matched-recall comparison. No workload savings or real-world AML benefit was established.

AP is sklearn Average Precision: precision weighted by increases in recall. It is **not trapezoidal PR-AUC**. New reports use `average_precision`; `pr_auc_average_precision` remains only as a compatibility alias for original artifacts. Test threshold tables are descriptive, never a selection criterion.

## Engineering investigation and decisions

| Area | Finding and decision |
|---|---|
| Imbalance and loss | 2,871 illicit of 26,381 labeled training nodes. GAT uses BCE positive weight 23,510 / 2,871 ≈ 8.189; logistic uses balanced class weights. Unknown nodes remain graph context. Retained for fixed replication; no oversampling duplicates graph nodes. |
| Features | Both models use 93 local anonymized features; exclude time and 72 preaggregated neighbor features. Local features may themselves summarize inputs/outputs, so the baseline is not devoid of relational information. |
| Normalization | Mean/SD fitted on training-period nodes only, including unknown training nodes; near-constant dimensions use scale 1. Held-out mutation test confirms training and validation threshold isolation. |
| Architecture/hyperparameters | Two GATConv layers, hidden width 16, two heads, dropout 0.1, Adam learning rate 0.005, weight decay 0.0005. Training loss is weighted; payment edges have no fabricated monetary weights. Retain this modest architecture to measure seed variability before introducing search complexity. |
| Operating point | Validation F2 maximized over thresholds 0.05–0.95 in 0.01 increments; lowest threshold wins ties. F2 emphasizes recall but does not impose a precision or recall guarantee. No threshold is picked from test performance. |
| Graph construction | Full-data inspection: 203,769 nodes, 234,355 directed edges; **0 duplicate edges, 0 self edges, 0 cross-time edges, 0 backward-time edges**. GATConv internally adds self-loops. CSV edges are preserved. |
| Neighborhood | Model uses incoming two-hop message-passing context. Case selection now applies the target-time cutoff, score threshold, stable ID tie-break and neighborhood bounds. No label-based case selection. |
| Temporal leakage | Train/validation edge cutoffs are 29/34; case inference cutoff is target time. No cross-time edges in the actual benchmark means full evaluation-period scoring matches target-time topology. Snapshot features do not establish intrastep real-time availability. |
| Model change | No new architecture or operating point was deployed. This hardening improves evaluation defensibility and investigation controls, not a claim of improved deployed detection accuracy. |

## Reproduction and artifacts

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate_seeds --out artifacts/multiseed-new-run
```

The output directory must be new. Each seed retains checkpoint, baseline parameters/background, scores, validation history, selected epoch/threshold, configuration and timing. `protocol.json` retains the training-code hash and runtime versions. The original remains in `artifacts/benchmark/` and `docs/benchmark_evaluation.json`; complete study output is in `docs/multiseed_evaluation.json`. The API/UI exposes the copied study as a separate report, with a dataset fingerprint check.

Recorded `training_total_seconds` includes optimization, validation/evaluation inference, logistic fitting and artifact writes up to report construction; excludes CSV ingestion. Stage timings in case reports include model loading/cache effects as documented there. None measures production throughput.


Measured totals for seeds 17/29/43 were **20.959 / 22.485 / 23.677 seconds**. Selected epochs were **24 / 25 / 25** and thresholds **0.74 / 0.59 / 0.73**. Original deployed checkpoint remains seed 17. No run's better test AP triggered a deployment or configuration change.


## Enhancement diagnostics — 2026-09-15

Deployed checkpoint and default threshold unchanged. A fresh seed-17 25-epoch run reproduced every original test metric exactly (the new report additionally names the existing AP value `average_precision`). Measured training total: 40.236 seconds on this run; no performance comparison across machines/load is implied. See docs/multiseed_evaluation.json.

Validation only (steps 30–34):

| Model / objective | Threshold | Precision | Recall | FP | FN |
|---|---:|---:|---:|---:|---:|
| gat / recall emphasis | 0.74 | 0.452830 | 0.893401 | 638 | 63 |
| gat / balanced | 0.74 | 0.452830 | 0.893401 | 638 | 63 |
| gat / precision emphasis | 0.89 | 0.669355 | 0.421320 | 123 | 342 |
| baseline / recall emphasis | 0.77 | 0.634772 | 0.920474 | 313 | 47 |
| baseline / balanced | 0.82 | 0.698087 | 0.864636 | 221 | 80 |
| baseline / precision emphasis | 0.90 | 0.833002 | 0.708968 | 84 | 172 |

The explorer includes all 91 thresholds with precision, recall, F0.5/F1/F2, FP/FN and alert counts. Objectives illustrate trade-offs, not regulatory rules. Threshold overrides use AML_DETECTION_THRESHOLD and are saved per case; the browser slider is exploratory only. Class weighting and the original feature policy remain justified by the documented imbalance and anonymous features; focal loss, broader GAT searches and semantic feature-group ablations were not promoted without stronger independent evaluation.

Calibration fits steps 30–32 and assesses 33–34. GAT Brier: raw 0.180209, sigmoid 0.057542, isotonic 0.058515. Logistic: raw 0.154048, sigmoid 0.059254, isotonic 0.052283. Reliability bins, ECE, log loss, fit parameters and caveats are recorded. These partitions already influenced checkpoint selection; no calibrator is deployed or claimed to transfer to later data. Raw scores remain labeled model scores. Brier combines discrimination and calibration effects.

Fixed-weight topology intervention on validation: GAT AP 0.542773 with original explicit edges, 0.492678 with them removed (internal self-loops retained). This modest sensitivity study is not retraining, a causal proof, or an architectural superiority test. Test labels/features are excluded; a mutation regression verifies diagnostic equality when all later-period labels/features are changed.

Reproduce with `.venv/Scripts/python.exe -m scripts.analyze_detection --out artifacts/new-validation-diagnostics` (new directory). Protocol saved before execution; machine-readable output preserved in docs/validation_analysis.json and artifacts/validation-diagnostics-final/. Browser SVG curves and tables use those results directly.

Primary method references: [sklearn precision-recall example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html), [calibration API and disjoint fitting guidance](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html), [calibration/Brier interpretation](https://scikit-learn.org/stable/auto_examples/calibration/plot_calibration_curve.html).
