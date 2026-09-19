# Evaluator runbook — Judge experience release 2026-09-17

The default landing page is Judge Mode. It presents four deterministic canonical cases; Technical Mode retains the full 20-case history and all research diagnostics. The verified journey is Dashboard → Case → Why Flagged → Network → Evidence → Investigation → Draft Report → Validation → Human Review → Audit. All benchmark nodes are transactions, directed edges are payment flow, and anonymized `local_feature_*` fields have no asserted business meaning.

## Setup and startup

From the repository root use the existing .venv, real Elliptic CSVs, artifacts/benchmark checkpoint and artifacts/flan-t5-small weights. For a new machine follow README setup and requirements-lock.txt; do not substitute synthetic data for the benchmark. Run heavy training/reproduction jobs sequentially, with loaded AML servers stopped on memory-constrained Windows hosts.

In a fresh PowerShell terminal (avoids inherited synthetic settings):

```powershell
Set-Location 'C:\Users\manju\OneDrive\Documents\AML'
./scripts/start.ps1 -Port 8002 -NarrativeProvider local
```

Open [the enhanced investigator desk](http://127.0.0.1:8002). Port 8002 was used for final verification because another application occupied a wildcard listener on 8000. Port is configurable. Wait for the real Elliptic banner and 203,769 nodes / 234,355 directed flows. Local mode requires no credential and explicitly identifies a shared local reviewer; token mode uses the configured analyst/reviewer token through **Access token**, kept in page memory. Never put actual tokens in the runbook.

## Canonical instance

Current enhanced case **ZEN-e5a3fceee610**, transaction **106776627**, model gat-7ad1b9876c4bdb71. Five nodes, five directed edges, model score 0.964630, threshold 0.74, high priority, 21 evidence records, Internal Prototype Readiness Score 67/100. The earlier canonical ZEN-e0fbc40247b5 and all 16 earlier cases remain unchanged. Historical instances lack some newly recorded structural fields and are labeled accordingly.

## Literal evaluator navigation

1. Search **ZEN-e5a3fceee610** in **Search cases**, select its case button, and start on **Summary**. Explain the five actual stage outputs and measured times. The investigation question is why a transaction/model neighborhood merits human inspection; no operational savings were measured.
2. In **Network**, read the model score and case threshold, separate from triage priority cutoffs. Show density 0.25, max fan-in/out 3/2, one weak component, no directed cycle, and 4/5 nodes above the model threshold. These describe the bounded neighborhood, not a proven typology or monetary concentration.
3. Set **Context depth** to Target only (1/5 nodes), then restore two hops. Set **Nodes** to Above case threshold (4/5), then restore All. The target is intentionally retained. Select transaction **106776627** with mouse or keyboard; inspect its dataset step, score, mask and degree. **Inspect anonymous source attributes** opens the 165 available numerical fields, with the first 93 marked as model inputs. No names, amounts or labels are reconstructed.
4. Click **E0005** in the node inspector. The evidence view shows the source feature CSV, transaction record and fingerprint. **Locate node 106776627** returns to the graph. Clicking an edge exposes source-edge citations. Filters affect the viewport, not the retained evidence.
5. In **Explanation**, show GNNExplainer feature/node/edge masks, original score and top-five-edge removal. Canonical score drop is about 0.03385; removing five edges removes all explicit case edges, a limited sensitivity check. SHAP below explains the independent logistic baseline in log odds, not the GAT. Neither is causal/legal proof.
6. In **Dossier**, inspect derived structural findings E0018–E0021, source chronology, model evidence, retrieval relevance and open questions. All canonical nodes are at **dataset time step 44**; their within-step order is unknown. KYC and sanctions show **unavailable**, with reasons and source/version fields. Do not show synthetic profiles as benchmark identities.
7. In **SAR draft**, point out **local**, **validated_constrained_extraction**, **DRAFT / NOT FILED**, and exact summary citations E0011/E0006. FLAN-T5 selects a constrained fact pair, while sections remain exact cited evidence. Open the claim editor to see supporting facts and current grounding; generation/revision provenance is inspectable. Do not edit the benchmark canonical during an automated demo; use the separate synthetic exercise below.
8. In **Compliance**, show the explicit checklist, findings and readiness factors/weights/reasons. Four of six scored checks pass, yielding 67/100; genuine identity context and live-data freshness remain unavailable. Mandatory human review has zero score weight and is always required. Passing consistency is not legal certification.
9. In **Review**, show required notes, approve/request changes/reject controls and **No human decision has been recorded**. This is the human decision point. No automated benchmark disposition was made.
10. In **Audit**, inspect stage transitions, revisions, actors, timestamps, event hashes and current case/model/evidence provenance. Integrity verified means consistency inside this database; no external trusted anchor makes it administrator-proof.
11. Clear search. In **More filters**, set creation date to **2026-09-15** and expand **Compare filtered cases** to inspect four enhanced instances, scores, nodes/evidence, explanation availability, providers, readiness and review/compliance states. Priority, status, model score, provider and readiness filters use real persisted values. Clear filters to see historical cases.
12. Expand **Benchmark evaluation & methodology**. Show original seed-17 and separate seeds 17/29/43 mean ± sample SD. Logistic wins precision/recall; GAT mean AP is higher. In the validation explorer switch F2 to F0.5: GAT threshold 0.74→0.89, validation precision 0.4528→0.6694 and recall 0.8934→0.4213. This slider does not deploy a threshold. Calibration/Brier diagnostics are exploratory and not deployed; test metrics did not improve.
13. Expand **System status & model provenance**, click **Load current status**, and inspect runtime/model details. Model ID, full hash, fingerprint, configuration, selected threshold, provider and database status are genuine; no secrets or fabricated passing-build assertion is shown. Filesystem mtime is not a verified training creation date.

## Four-case reproduction

Case IDs: **ZEN-e5a3fceee610**, **ZEN-a59323abee0f**, **ZEN-ebd9e11c023e**, **ZEN-5acf0e22710a**. Transaction selection: 106776627, 218047279, 219679769, 195439532. UUIDs change on recreation; transaction targets, checkpoint and selection rule reproduce. Selection is label-independent: evaluation-period time, model threshold, descending score/ID tie-break, incoming two-hop neighborhood bounds 3–1500, skipping already covered targets.

```powershell
$env:AML_LLM_PROVIDER='local'
.\.venv\Scripts\python.exe -m aml.cli demo --cases 4
.\.venv\Scripts\python.exe -m scripts.verify_capstone --out artifacts/new-evaluator-reproduction
```

The first appends cases and updates the manifest; preserve its prior version before intentional future demonstrations. The second requires a new directory and validates four cases in a fresh database, source checks, no decisions, audit integrity and persistence across pipeline restart.

## Isolated synthetic editing/review exercise

Prepare a new case with the synthetic helper. No benchmark record is modified:

```powershell
.\.venv\Scripts\python.exe -m scripts.prepare_ui_test --db artifacts/enhancement-ui-test.db --reference-fixture tests/fixtures/reference_snapshot.json
$env:AML_DATA_DIR='artifacts/ui-test/raw'
$env:AML_ARTIFACT_DIR='artifacts/ui-test/model'
$env:AML_DB_PATH='artifacts/enhancement-ui-test.db'
$env:AML_REFERENCE_FIXTURE='tests/fixtures/reference_snapshot.json'
./scripts/start.ps1 -Port 8003 -NarrativeProvider extractive
```

Open port 8003 and confirm **SYNTHETIC TEST DATA**. Dossier shows **SYNTHETIC DEMO KYC** / **SYNTHETIC DEMO SANCTIONS**, explicit fixture mapping, synthetic match and source/version. These are excluded from benchmark/LLM claims and cannot satisfy genuine-identity readiness.

In **SAR draft → Edit claims with supporting evidence**, temporarily change Claim 1.1 to `SYNTHETIC NEGATIVE TEST: unsupported invented claim.` Save and wait for the new revision. The unsupported finding must be visible and Review → Approve disabled. Request changes with explicit synthetic notes. Restore the exact cited source fact and save. Compare saved narrative revisions, then exercise simulated approval/rejection with notes explicitly saying this is a synthetic control test. Final state locks editing and review; Audit retains every step.

Verified instance **ZEN-a0166b7268ee**: unsupported revision 13; request changes revision 14; repaired revision 15; simulated approval revision 16. Three distinct narrative snapshots remain. This is an automated synthetic test, not an actual human AML judgment. Create a new synthetic case for another exercise; do not unlock this final case.

## Failures and interpretation

A failed stage shows its reason and retry control while earlier completed outputs remain stored; Summary exposes completed/pending/failed state. If startup lacks a checkpoint/data/provider, fix the configured dependency and retry. Do not interpret a failed or partially completed case as success. Browser/API tests and unit tests cover failures, stale writes, unsupported text and locked states.

Modest detection precision, anonymous features, previously seen evaluation data and no genuine entity linkage remain the key limits. Read MODEL_CARD.md, SYSTEM_CARD.md, EVALUATION.md and IMPLEMENTATION_DECISIONS.md before making stronger claims. SubgraphX/GAT-SHAP/live reference feeds/production AML are explicitly deferred or unverified.
