# Validation record

## Current status

Test status for the current repository state:

- **Backend (pytest): 52 passed, 3 upstream warnings.**
- **Presentation / UI (`node --test tests/ui_presentation.test.cjs`): 8 passed.**
- **JavaScript syntax check (`node --check`): clean** on `web/app.js`, `web/workstation.js`, `web/judge.js` and `web/presentation.js`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp artifacts/new-pytest-run -o cache_dir=artifacts/pytest-cache
node --test tests/ui_presentation.test.cjs
node --check web/app.js
```

The backend count is the current verified result for the project environment; it was **not re-run** while refreshing this document, because the local `.venv` is not part of the repository. The presentation suite **was re-run** for this refresh and reports **8** passing tests (the test file defines 8 tests). Earlier values in the historical sections below (36 / 46 / 48 passed) are superseded by this current status.

## Enhancement acceptance — 2026-09-15

New tests cover threshold counts and finite-score validation; validation-period calibration partitions; test-label/feature mutation isolation; degree/cycles/concentration; structural-evidence tampering; explicit synthetic reference isolation; case-scoped/deduplicated/filtered retrieval; immutable generation provenance and stale revisions/history; status/model/source/history authorization and secret exclusion; threshold overrides and credential-bearing URL rejection. Existing source/claim/review/audit/encryption/RBAC/TLS/failure tests remain.

Fresh seed17 training exactly reproduced every original test metric. Original checkpoint/report/multi-seed files, unchanged training/data/explainer source, and all16 previous case payloads/audits pass preservation checks. Added average_precision is an alias for the already measured original AP. Four enhanced main cases and four fresh-database cases pass every demo/source/audit/restart check. All20 main cases retain zero decisions.

Browser validation used actual local API state at ports8002 and8003. Confirmed canonical briefing; 5-node network; depth/score filters; mouse and keyboard inspection; source attributes; evidence-to-graph round trip; structural findings and unavailable genuine references; separate GNNExplainer/baseline SHAP; local constrained draft; checklist/readiness; review no-decision state; audit; four-case creation-date comparison; model/status whitelist; validation F0.5 threshold and calibration tables. Mouse capture and narrow-screen overflow were fixed and retested; document width637px within652px viewport. No console errors observed during checked flows.

Synthetic case ZEN-a0166b7268ee confirmed fixture labels, unsupported saved claim at revision13 with approval disabled, request changes14, exact-fact repair15, three narrative snapshots, simulated approval16, valid audit and final lock after page reload. All simulated notes explicitly identify synthetic control testing. No benchmark review was simulated.

Evidence: docs/validation_analysis.json, docs/case_validation.json and docs/demo_manifest.json. Profile: seven identical source-check outputs; median0.447428s original vs0.000949s cached; index construction0.242764s separately measured. No whole-application throughput claim.

Failed attempts retained: backup-test discovery before pytest.ini; optional matplotlib plotting unavailable; concurrent heavy checks hit Windows paging/memory limits and were rerun sequentially; preservation report schema equality initially flagged the added AP alias, then exact original metric fields were compared. No failing attempt is represented as a pass. Three upstream deprecation warnings remain. Live Ollama, production load/security, genuine reference screening and prospective calibration remain unverified.

## Historical validation record (prior release)

# Verification record — 2026-09-14

## Final software and data checks

Final full suite: **36 passed, 3 upstream deprecation warnings, 14.52 seconds**. Original inspection baseline: 26 passed in 8.24 seconds. A first attempt failed at fixture setup due to Windows permission on the old default pytest temp folder; no product failure was hidden, and using a new workspace basetemp resolved it. Reproduce with a new directory:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp artifacts/new-verification-tests -o cache_dir=artifacts/pytest-cache
node --check web/app.js
.\.venv\Scripts\python.exe -m aml.cli inspect
```

All passed locally. Tests cover ingestion, topology sensitivity, train-only scaling, held-out mutation isolation for GAT and baseline, GNNExplainer, SHAP additivity, all pipeline stages, evidence/retrieval, unsupported content/headings, missing references, model mismatch, source-text tampering, checksum mismatch, mandatory-disclosure deletion, summary citations, seed statistics, label-independent selection, failure/resume, stale revisions, all three review outcomes, final-state lock, blank notes, persistence/audit, encryption, role/host/origin restrictions and certificate-verified HTTPS. Synthetic graphs test software behavior; their metrics are not benchmark evidence.

Full real-data inspection verified the declared three-file manifest against actual bytes and found 203,769 nodes/234,355 edges, zero duplicate/self/cross-time/backward-time source edges. `docs/dataset_profile.json` and `docs/dataset_manifest.json` retain the result/provenance. A self-authored local manifest is traceability, not independent publisher authentication.

## Model and four-case verification

Real 25-epoch seed runs **17/29/43** completed with original configuration. Training/evaluation totals were **20.959/22.485/23.677 seconds**, excluding CSV loading. Selected epochs **24/25/25**, validation-F2 thresholds **0.74/0.59/0.73**. Seed 17 exactly reproduced original reported metrics. AP, per-seed values and sample SD are in `EVALUATION.md` and `multiseed_evaluation.json`. The already observed temporal test was reused only for fixed replication, not model/threshold tuning; no new untouched evaluation dataset is claimed.

Four current connected benchmark cases, using real local FLAN-T5 constrained generation, passed every pipeline stage, source validation, consistency and audit checks and entered `awaiting_review` without decisions. Canonical **ZEN-e0fbc40247b5**, transaction **106776627**, has five nodes/five edges and 17 evidence records. All **16 main-database cases** remain unreviewed with valid audit chains; historical cases retain original snapshots rather than silently acquiring new controls. `case_validation.json` and `demo_manifest.json` retain outputs/timings.

Current-case pipeline times: **9.557/5.205/4.688/3.053 seconds**; narrative times **5.182/3.491/3.465/1.893 seconds**. These exclude CSV/checkpoint startup and human review; first narrative includes local model loading, later cases reuse cached model objects. Detection timings include inference and explanation together, not standalone inference latency.

Final independent recreation using `scripts.verify_capstone --out artifacts/capstone-release-verification` generated the same four transaction targets in a new database, checked actual model flags/source checks/audits and reloaded identical case payloads through a fresh Pipeline instance. All checks passed. Pipeline times: **5.090/2.234/1.779/1.559 seconds**; report: `reproduction_validation.json`. Random case UUIDs appropriately differ. Earlier reproduction artifacts remain preserved.

## Browser workflow exercised

The actual loopback application was started and inspected through browser controls:

- Real 16-case queue and original benchmark metrics loaded from the backend.
- Canonical Network showed five transactions, score 0.964630, threshold, triage and explicit model/case distinction.
- Explanation showed ranked nodes/edges/features, score deletion sensitivity and baseline-only SHAP. Canonical score drop was about 0.03385; this tiny graph loses all five explicit edges, so the check is not a strong validation of the ranking.
- SAR draft showed a real local two-fact summary, DRAFT / NOT FILED and validated citations. Clicking E0006 opened the source edge `106344367->106776619` with the dataset fingerprint.
- Dossier showed actual step-44 chronology and unavailable KYC/sanctions. Compliance showed 67/100 Internal Prototype Readiness Score with factor weights/reasons, mandatory review and zero current consistency findings.
- Benchmark Review displayed no decisions. Audit displayed integrity verified, intake, all stage events, timestamps and hashes.
- Expanded evaluation displayed the separate three-seed table and explicitly disclosed the baseline's precision/recall advantage and reused test period.
- Separate port-8001 synthetic case **ZEN-99c0f71da2fa** visibly carried the SYNTHETIC TEST DATA banner. Explicit automated-test notes were entered; request changes persisted at revision 13, simulated approval at revision 14, and all subsequent decision buttons were disabled. Persisted notes/audit are in `synthetic_review_validation.json`. These are controlled software-test actions, not human AML judgments.
- The final benchmark server was restarted after code changes; persistence and queue loaded again. This is desktop browser verification, not exhaustive device/accessibility or penetration testing.

## Security/control matrix

| Control | Default / optional | Verification / limit |
|---|---|---|
| Loopback client restrictions and trusted Host | Default without tokens | Client/Host restrictions in code; DNS-rebinding Host rejection tested. Demo remains local HTTP. |
| Same-origin mutations | Default | Foreign Origin rejection tested. |
| CSP, no-store, nosniff | Default | HTML, JS and API response headers asserted. UI dynamic text passes through HTML escaping; no comprehensive XSS audit claimed. |
| Bearer analyst/reviewer roles | Optional | API authorization, missing tokens and role separation tested; roles do not identify individual staff. |
| Fernet payload encryption | Optional | Encrypted persistence/readback and test-marker absence tested. Metadata and public CSV/models are outside this encryption boundary; no enterprise key management. |
| HTTPS | Optional | Real Uvicorn TLS with explicitly trusted test certificate verified. Default demo HTTP is not described as encrypted transit. |
| Audit hashes | Default | Snapshot/current-payload tampering blocks review; all current benchmark chains verified. Administrator rewriting of the whole chain is outside this protection. |
| Review governance | Default | Current revision, meaningful notes, unsupported-claim blocking, scope-disclosure enforcement, final-state locking and explicit retry tested. Approval does not file a SAR. |

## Limits and evidence bundle

No live banking, KYC/sanctions, GAT-specific SHAP, SubgraphX, free-prose validation, external fresh benchmark or production throughput is verified. Dataset context is historical and anonymous. The local LLM's actual prompt and weight hash, original checkpoint hash and training configuration are in `model_narrative_provenance.json`. Proposal alignment and claim audit are in `IMPLEMENTATION_DECISIONS.md`; canonical walkthrough in `CAPSTONE_DEMO.md`. Capstone readiness is limited to the demonstrated research workflow and its tested controls.
