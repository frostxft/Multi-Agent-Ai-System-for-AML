# Team Zen model card — 2026-09-15

## Purpose and intended use

Research demonstration of transaction-node classification and investigator evidence navigation on Elliptic. Not a supervised ring detector, criminal finding, production AML control, or SAR filing recommendation. The deployed model is unchanged by the enhancement release.

## Data and inputs

Elliptic: 203,769 transaction nodes, 234,355 directed payment edges, 49 dataset time steps. Labels: 4,545 illicit, 42,019 licit and 157,205 unknown. Unknowns participate in graph context only. Both models use 93 local anonymous numerical attributes; exclude time and 72 preaggregated neighbor attributes. Some local attributes already summarize input/output relationships. No genuine names, customer identities, amounts or calendar timestamps are available to investigators.

Train steps 1–29; validation 30–34; evaluation 35–49. Training-only scaling includes unknown training nodes. Edges are cutoff by period. Case inference uses the target's dataset time step. All source edges in the inspected dataset connect same-step transactions; no within-step sequence is inferred.

## Architecture, training and output

Two PyG GATConv layers, hidden width 16, two attention heads, dropout 0.1. Adam learning rate 0.005, weight decay 0.0005, weighted binary cross entropy with positive weight 23,510/2,871. Seed 17, 25 epochs, selected epoch 24 by validation AP. Logistic comparator: balanced class weights, C=1, maximum 1,500 iterations. Output is an **uncalibrated illicit-class model score**, not probability of money laundering.

Default threshold 0.74 maximizes validation F2 over 0.05–0.95 in increments of 0.01; ties choose the lower threshold. Configured AML_DETECTION_THRESHOLD overrides affect new cases and record both default and override provenance. Priority cutoffs 0.5/0.8 are separate triage rules, not regulatory thresholds.

## Evaluation

| Model | Seed-17 precision | Recall | AP | Threshold |
|---|---:|---:|---:|---:|
| GAT | 0.159810 | 0.620499 | 0.210292 | 0.74 |
| Logistic | 0.191597 | 0.804247 | 0.200893 | 0.77 |

GAT three-seed mean ± sample SD: precision 0.154474 ± 0.008829, recall 0.629732 ± 0.046855, AP 0.233925 ± 0.020622. Logistic results are identical across seeds 17/29/43; zero seed SD does not imply zero population uncertainty. GAT has higher mean AP; logistic wins precision and recall at the chosen operating points. No statistical superiority, matched-recall benefit or operational savings established. AP is sklearn average precision, not trapezoidal area. The evaluation period was previously observed; these are fixed replications, not a newly untouched evaluation.

## Enhancement diagnostics

Validation-only threshold curves/tables compare F2/F1/F0.5, precision/recall, false positives and false negatives. At GAT threshold 0.74, validation precision is 0.452830 and recall 0.893401. Precision-emphasizing F0.5 selects 0.89, trading recall down to 0.421320 for precision 0.669355. These are validation results, not improved test results.

Sigmoid/logistic and isotonic calibration fit steps 30–32 and assess 33–34. Both improve Brier error on that partition, but checkpoint selection already used the full validation period. **No calibrator is deployed.** Reliability bins, log loss, ECE and fit parameters are inspectable. Calibration transfer requires independent assessment. Fixed-weight removal of all explicit edges reduces validation AP from 0.542773 to 0.492678 (self-loops remain); this is an inference intervention, not a retrained graph-vs-tabular experiment.

## Explanations and limitations

GNNExplainer optimizes graph-model masks with score reproduction and deletion checks. SHAP explains only the logistic baseline in log odds; these are different models. Masks are neither causal/legal proof nor calibrated explanation confidence. Weak or negative deletion effects remain visible. Anonymous features limit human semantic interpretation. Low precision, dataset shift, seed variability and lack of prospective ground truth constrain deployment. No fiat banking transfer, fairness across customer groups, drift validation or real identity linkage is established.

## Version and provenance

Model ID: gat-7ad1b9876c4bdb71. Dataset fingerprint: 903ac5dfcabafb86638bbceddef49530bdad2743c6cfe71a7d1c78bf0da9f043. Full checkpoint SHA256, training configuration, evaluation and filesystem modification time are available in /api/model; filesystem time is not a verified training creation timestamp. See EVALUATION.md, benchmark_evaluation.json and multiseed_evaluation.json for full measured results.
