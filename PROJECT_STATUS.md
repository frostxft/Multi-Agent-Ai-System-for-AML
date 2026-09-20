# Team Zen engineering status

## Final release repository cleanup — 2026-09-19

- Removed the local virtual environment (`.venv/`) and all regenerable caches (`__pycache__/`, `*.pyc`/`*.pyo`, pytest basetemp/cache outputs). Reproduce the environment with `./scripts/setup.ps1` + `requirements-lock.txt`.
- `artifacts/` now holds only final runtime/deliverable material: `artifacts/benchmark/`, `artifacts/flan-t5-small/`, `artifacts/cases.db` (20 runs), `artifacts/claim-audit.txt` and `artifacts/capstone-release-verification/`. Historical snapshots/reproductions (`pre-enhancement-20260915/`, `enhancement-seed17-verified/`, `enhancement-four-case-reproduction/`, `ui-test/`), the `artifacts/archive/` archive, test logs and stale enhancement validation records were removed; none were required by the app, tests, startup or setup.
- Removed the large FLAN-T5 Kaggle source archive `artifacts/flan-t5-small-kaggle.zip` (1.83 GB): the extracted model is complete and the app loads only the folder at runtime; `download_llm.py` / `download_llm_direct.py` reproduce it. The benchmark source archive `data/elliptic/elliptic.zip` is retained (used by `scripts/unpack_data.py`).
- Removed superseded documentation (`docs/ENHANCEMENT_GAP_ANALYSIS.md`, `docs/REPOSITORY_CLEANUP.md`, `docs/FINAL_RELEASE_AUDIT.md`, stale enhancement validation JSON records) and the obsolete `scripts/verify_enhancement.py`; surviving docs were updated to remove dangling references.
- No functional change: backend **52 passed**, presentation **8 passed**, `node --check` clean, live API/audit/enrichment checks passed, SAR-style PDF export re-verified.

## SAR-style report export — PDF pagination polish (2026-09-19)

- Removed an awkward page break that left **Provenance / Audit** alone on a mostly-blank page with the technical appendix starting on the next page. Provenance / Audit and the **Technical Provenance & Validation** appendix now flow together, and **Supporting Evidence** starts on a fresh page, giving natural pagination: title/case/summary/context → evidence → enrichment/narrative/validation/review/audit → technical appendix.
- Added break hygiene (headings stay with content, table rows never split, footer not orphaned). No content, evidence, narrative, validation, provenance or disclaimer changed; traceability intact. Assets re-pinned to `?v=30` (the stylesheet had been stale at `?v=27`).
- Validation: fresh PDFs regenerated via headless Chrome for two cases; no near-empty page and no clipped text (all evidence IDs, full narrative, full claim-validation and both disclaimers present; no filesystem paths). Backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean.

## SAR-style report export — provenance/professionalism polish (2026-09-19)

- The exported report no longer contains personal/local filesystem paths. Benchmark evidence sources previously shown as `C:\Users\...\...\elliptic\raw\*.csv` now read **"Elliptic benchmark transaction record"** / **"Elliptic benchmark payment-flow record"**, with the record ID and version preserved.
- The full benchmark fingerprint is no longer prominent: the Support Evidence table shows a short version reference and the Provenance / Audit summary a short dataset reference. Full model ID, dataset fingerprint and per-evidence versions are retained in a subdued **Technical Provenance & Validation** appendix (evidence provenance + claim → evidence → source validation tables).
- Traceability is intact (all evidence IDs, facts, record IDs, versions and provenance relationships), and the disclaimers **"Draft only · Human review required · Not a filed SAR"** and **"Human investigator retains final authority."** are unchanged. No backend/model/evidence/schema/API/review/audit change; assets at `?v=29`.
- Validation: two real PDFs generated via headless Chrome and text-verified (no paths; all evidence IDs, full narrative, sanitized labels, demo-enrichment and disclaimer text; fingerprint only in the technical appendix); backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean.

## SAR-style report export — 2026-09-19

- **Evidence & Report → SAR Narrative** now has an **Export SAR-style Report** action that composes a full SAR-style investigation report from the selected case's live API data and opens the browser print dialog (save-as-PDF). Dependency-free: no PDF library, no new runtime dependency; uses a print-only `#print-report` container plus `@media print` CSS so the on-screen layout and scrolling are unchanged.
- **Report sections:** Case Information · Executive Summary · Why This Case Needs Review · Network / Activity Context · Supporting Evidence (with source/provenance) · Investigation Enrichment (synthetic demo KYC/sanctions, when present) · Missing Information & Limitations · SAR-style Narrative (with citations) · Compliance / Validation · Human Review Status · Provenance / Audit.
- All content is **case-derived** (no hardcoded case values); labelled **"Draft only · Human review required · Not a filed SAR"**. The action only renders the report — it performs no review/reopen call, so **Review & Audit remains the single human-decision mutation surface**.
- No backend/model/evidence/threshold/schema/API-contract change. Validation: backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean; output verified dynamic across two distinct cases (no cross-case leakage, no truncation); assets served at `?v=28`.

## Final Judge UX & Repository Status — 2026-09-19

- **Final EOI workflow (judge-facing):** Detection → Risk Triage → Investigation → SAR Narrative → Compliance → Human Review → Audit. The four-tab **case workspace** (Overview / Network & Explanation / Evidence & Report / Review & Audit) is the navigation; explainability is not a separate stage (GNNExplainer inside Detection; SHAP = Compliance baseline cross-check).
- **Judge Mode:** non-technical by default ("AI detection", "Transaction network", "What influenced this case", "Model score", "Independent model cross-check", "SAR-style draft", "Compliance validation", "Human review"). Progressive disclosure for all technical detail.
- **Technical Mode:** retains GAT, GNN, GNNExplainer, SHAP logistic-baseline, model ID, dataset fingerprint, metrics, thresholds, evidence mappings, provenance, validation internals and audit metadata — unchanged and accurate.
- **Dynamic data:** all case-specific content (case/transaction/evidence IDs, scores, counts, network relationships, demo KYC/sanctions values, claims, report text) is derived from the selected case and its API; no hardcoded case content.
- **Human review:** Review & Audit is the single mutation surface (Approve / Request changes / Reject / Reopen for review); Evidence & Report shows a dynamic status summary and links to Review & Audit.
- **Audit:** persistent hash-linked trail; valid for all cases; no history deleted or rewritten.
- **Repository cleanup:** "Repository cleanup removed only verified generated, temporary, or obsolete files. Required project artifacts were preserved." Removed: `aml/__pycache__/`, `scripts/__pycache__/`, `tests/__pycache__/`, `artifacts/release-server.log`, `artifacts/release-server-error.log`, `artifacts/final-consistency-verification/`. The empty root `.pytest_cache/` is filesystem-locked and remains (gitignored).
- **Validation:** backend **52 passed, 3 warnings**; presentation **8 passed**; `node --check` clean; application started from the cleaned repository; API smoke + multi-case dynamic render passed.
- **Remaining future work:** live KYC · live sanctions · SubgraphX · calibrated probabilities · production bank integration · prospective evaluation · demonstrated false-positive reduction · identity resolution · drift monitoring · federated deployment · automatic disposition.
- **Known limitations:** uncalibrated scores; anonymous Elliptic features; no live KYC/sanctions/identity; no filed SAR; no demonstrated ROI/false-positive reduction; reused evaluation period; the `torch.jit.script` FutureWarning originates from PyTorch Geometric (upstream).

## EOI Alignment Status — 2026-09-19

### Implemented
- **Detection** — real Elliptic transaction graph; two-layer PyG GAT; model score; GNNExplainer local graph explanation; incoming two-hop transaction context.
- **Risk triage** — configurable priority thresholds over the model score; network-structure signals; separate from the model alert threshold.
- **Investigation** — case-scoped evidence retrieval/deduplication; investigation dossier; source-linked evidence; open questions.
- **SAR narrative** — constrained local FLAN-T5 extractive summary (or deterministic extractive mode); evidence-grounded draft with clickable citations.
- **Compliance** — consistency/grounding validation, source rechecks, provenance, readiness checks, and the SHAP baseline cross-check.
- **Human review** — approve / request changes / reject, required notes, revision checks, final-state locking, and controlled **Reopen for review** (new revision; prior decisions preserved).
- **Audit** — persistent hash-linked audit trail of stages, revisions and review actions.

### Synthetic / Demo
- **Demo KYC** and **static demo sanctions screening** (`aml/demo_enrichment.py`; deterministic per transaction; clearly labelled `DEMO / SYNTHETIC PROTOTYPE ENRICHMENT`; **not** from the Elliptic benchmark or live systems; **never** a GAT model input).

### Benchmark
- Elliptic Bitcoin benchmark only: anonymous transaction nodes and directed payment-flow edges; no live banking data, real customers, monetary amounts, dates or identities; features are anonymised with no asserted financial meaning. Held-out metrics are modest and uncalibrated; the evaluation period was reused.

### Human Governance
- **Review & Audit is the single mutation surface for human decisions** — **Approve / Request changes / Reject** with required investigator notes, plus controlled **Reopen for review** (reason required, new revision, prior decisions preserved). **Evidence & Report** displays the dynamic review status and links to Review & Audit; it does not duplicate decision controls. Persistent audit trail; approval records an internal prototype disposition and does not file a SAR.

### P2 investigation notes (2026-09-19)
- **Rejected test case** `ZEN-5acf0e22710a` — already returned to `awaiting_review` (revision 17) through the legitimate reopen workflow; its approve/request-changes/reject/reopen history is preserved and the audit chain is valid. No database manipulation used.
- **readiness_score** — the list endpoint's canonical field is `readiness` (value 67); a `readiness_score` alias now exposes the same derived value. No validation logic changed.
- **torch.jit.script deprecation warning** — originates from PyTorch Geometric (upstream), not this codebase; the model is unchanged and the warning is documented rather than suppressed.

### Technical Explainability
- **GNNExplainer** — local GAT explanation (feature/edge masks, intervention sensitivity). **SHAP** — independent cross-check for the **logistic baseline only**, not the GAT.

### Future Work
- Live KYC integration · live sanctions screening · SubgraphX explainability · calibrated probability scores · production bank/system integration · prospective (untouched) evaluation · demonstrated business false-positive reduction · production identity resolution · drift monitoring · federated/privacy-preserving deployment · automatic disposition.

### Known Limitations
- No live KYC, no live sanctions, no actual SAR filing, no demonstrated production ROI/false-positive reduction, no prospective evaluation, uncalibrated scores, anonymous features. **SubgraphX is not implemented** (verified in the repository; GNNExplainer supplies graph attribution).

### Validation
- Backend: **52 passed, 3 warnings**. Frontend presentation: **6 passed**. `node --check` clean on all four web scripts. Multi-case dynamic rendering verified (distinct per-case signatures). No model, dataset, evidence, provenance, schema, threshold or API contract changed.

## Capstone PPT alignment — demo KYC / sanctions enrichment (2026-09-18)

Added the prototype-level components the Capstone PPT describes without changing the frozen engine. A new isolated module `aml/demo_enrichment.py` returns deterministic, clearly-labelled **synthetic demo KYC** (demo customer ID, country, account type, risk attribute) and **static demo sanctions screening** (result, reference, screening timestamp, match status) for a case's transaction, exposed read-only at `GET /api/cases/{id}/demo-enrichment`. It is **never a GAT model input**, never changes a model score, and is never written into benchmark evidence or provenance; the synthetic demo sanctions list contains only fictional IDs so the demo reports "no match" rather than inventing a hit. Judge Mode shows an "Investigation enrichment" panel, validation gains demo KYC/sanctions availability rows, and the report is labelled a **SAR-style draft (DRAFT · NOT FILED)** with a demo-enrichment section. The architecture view and workflow now read Detect → Triage → Investigate → Report → Validate → Human review → Audit, with KYC/sanctions explicitly marked DEMO / SYNTHETIC PROTOTYPE ENRICHMENT. Tests: **50 backend** (2 new) + **6 presentation** passed; GAT, dataset, evidence and provenance unchanged.

## Current Stage: FINAL CAPSTONE RELEASE — VERIFIED (2026-09-18)

Final release audit complete and the application was started and exercised over HTTP. Final tests: backend **48 passed** (3 upstream warnings), frontend presentation **5 passed**, `node --check` clean. Live demo at `http://127.0.0.1:8002` returned the canonical four-case collection in manifest order, 20 stored runs, canonical `ZEN-e5a3fceee610` / transaction 106776627 (5 nodes, 5 edges, 21 evidence, score 0.964630, model `gat-7ad1b9876c4bdb71`), valid audit chain (12 events), and zero review decisions. Canonical startup: `./scripts/start.ps1 -Port 8002 -NarrativeProvider local`. Known limitations and frozen components are unchanged. See docs/VALIDATION.md. This remains a research prototype, not production AML.

## UI/UX redesign — Judge workspace (2026-09-18)

Frontend presentation, layout, styling and interaction patterns only; the backend, models, metrics, thresholds, case-selection, evidence/retrieval, audit/review schemas and agent architecture are unchanged. Judge Mode now follows a four-step primary workflow — **Overview → Network & Explanation → Evidence & Report → Review & Audit** — with a compact investigator queue, a sticky case header (model score as decimal `0.965`, alert threshold, connected context, evidence), a visual "Why was it flagged?" bullet list, a stage timeline, a legended interactive network, scannable evidence cards, a report-styled draft, a prominent human-review panel, and a chronological audit timeline. Technical depth (GNNExplainer, SHAP baseline, threshold/calibration explorer, multi-seed evaluation, provenance, raw JSON) moved behind progressive disclosures and Technical Mode. Model-score language uses decimals and never calls a score a probability; anonymized features remain labeled. The `reasons()` presentation text was rewritten and `tests/ui_presentation.test.cjs` updated to match (same intent, new wording). Validation after redesign: backend **48 passed**, presentation **5 passed**, `node --check` clean on all four web scripts, and the four canonical cases still resolve against the live server.

## Judge experience milestone — complete (2026-09-17)

Two presentation modes, curated demo collection, plain-language case journey, source-focused evidence and progressive technical disclosure are implemented. Fresh four-case reproduction, full browser journey, responsive check, and final tests are complete. See docs/JUDGE_UX_DECISIONS.md.

## Re-verification — 2026-09-18

Final Judge/Demo hardening was re-verified against the current repository rather than assumed from the status file. No code or artifacts changed; no new feature, dependency or data was introduced. Confirmed: backend suite **48 passed** (3 upstream warnings), frontend presentation suite **5 passed**, `node --check` clean on all four web scripts. Runtime API verification against the real Elliptic graph and GAT checkpoint returned the expected state: demo-collection `available` with canonical `ZEN-e5a3fceee610` plus three cases in manifest order, 203,769 nodes / 234,355 directed flows (`benchmark`), 20 persisted runs, canonical transaction 106776627 at score 0.964630 with 5 nodes / 21 evidence records, audit integrity valid, and zero recorded review decisions. Held-out metrics re-read from `evaluation.json` match the recorded values (GAT P 0.159810 / R 0.620499 / AP 0.210292; logistic P 0.191597 / R 0.804247 / AP 0.200893; three-seed GAT mean ± sample SD unchanged). The full browser walkthrough remains as recorded on 2026-09-17 and was not re-run in this environment. Judge Mode — VERIFIED.

## Repository cleanup — 2026-09-18

Final hygiene pass, no functionality changed. Removed 23 regenerable paths (Python `__pycache__`, root `.pytest_cache`, 14 pytest basetemp outputs, 5 pytest cache directories, an empty `hf_cache`); the empty root `.pytest_cache` could not be deleted due to a filesystem lock and remains ignored. Archived (not deleted) 7 historical snapshot/reproduction/diagnostic directories, 5 historical reports/manifests, the superseded `judge-ui-test.db`, and 48 temporary logs under `artifacts/archive/`. Preserved all source, docs, real Elliptic data, `artifacts/benchmark/` (checkpoint/evaluation/manifest), `artifacts/cases.db` (20 runs), `artifacts/flan-t5-small/` and both large source archives (`data/elliptic/elliptic.zip`, `artifacts/flan-t5-small-kaggle.zip`), plus every artifact referenced by docs/code. Canonical demo port standardized to **8002** (`./scripts/start.ps1 -Port 8002 -NarrativeProvider local` → `http://127.0.0.1:8002`). `.gitignore` extended for logs, Python caches, and editor/OS files. Post-cleanup: backend **48 passed**, presentation **5 passed**, `node --check` clean, and runtime demo verification unchanged (canonical four cases, 20 runs, valid audits, zero decisions). (Superseded by the 2026-09-19 final cleanup above.)

## Previous verified stage — 2026-09-15

**Enhanced capstone demonstration verified.** This release improves investigation usability, evidence inspection and evaluation defensibility while preserving the deployed detector and every prior case. It remains a research prototype, not production AML, a proven laundering-ring classifier or a legally sufficient SAR system.

## Enhancements and rationale

- Validation-only 91-point threshold tables/curves and F2/F1/F0.5 objectives explain alert trade-offs. New-case threshold overrides retain checkpoint/default/configuration provenance; triage thresholds remain separate.
- Raw-score reliability, temporal validation sigmoid/isotonic calibration and fixed-weight topology intervention make model weaknesses inspectable. No calibrator, new architecture, focal loss or test-driven threshold was deployed.
- Actual local degree, density, fan-in/out, weak components, cycle presence, path depth, dataset time steps and neighbor-score concentration add four versioned structural evidence records, recomputed during validation.
- Graph depth/score/time/edge filters, mouse/keyboard inspection, source attributes and citation-to-node navigation join the investigation without inventing identities or chronology. Full stored evidence is retained.
- Dossier separates source facts, model/derived outputs, reference context, open questions and investigator notes. Retrieval enforces case scope, metadata filters, deduplication and positive relevance; unrelated zero matches are omitted.
- Typed KYC/sanctions protocols and deterministic synthetic snapshot adapters show an honest extension boundary. Explicit synthetic entity linkage is mandatory, benchmark fixture configuration is rejected, and genuine reference context stays unavailable.
- Structured claim editor, original generation provenance, revision metadata/history, explicit checklist and blocking findings support controlled review. Queue filters/comparison and system/model provenance improve evaluator inspection.
- Source-check index and cached dataset profile avoid repeated graph scans. Mouse selection/pan interception and narrow-screen overflow found during browser verification were fixed.
- Bearer parsing, endpoint credential rejection and server-owned draft provenance were hardened with regression coverage. No new runtime dependencies; existing lockfile retained.

## Actual validation

Baseline: **36 passed, 3 warnings, 51.80s**, before substantive changes. Final: **46 passed, 3 warnings, 29.98s**. JavaScript syntax checks passed for both files. Tests cover new threshold/calibration isolation, structure tampering, synthetic reference isolation, retrieval, provenance, auth/source/history routes, configuration and existing review/audit/security controls.

Fresh 25-epoch seed-17 training reproduced all original test metrics exactly; only the existing AP alias was added to the report schema. Main four-case local-FLAN-T5 demonstration passed all checks; another four cases in a fresh database reproduced selected transactions and persisted across pipeline restart. Original checkpoint, evaluation/multi-seed reports and all 16 previous case payloads/audits remain unchanged. All **20** main cases have valid audits and **zero review decisions**.

Browser checks covered briefing, graph filters/mouse/keyboard, evidence/source navigation, dossier, separate explanations, local draft, checklist, readiness, comparison/date filters, threshold/calibration explorer, status/provenance and audit. Separate synthetic ZEN-a0166b7268ee persisted unsupported revision 13 (approval blocked), request changes 14, repaired revision 15, simulated approval 16; final editor/review controls locked after reload. Three distinct narratives retain history. No browser console errors were observed during checked flows.

Initial concurrent validation exhausted Windows memory/paging; failed logs are retained and excluded from passes. Heavy runs succeeded sequentially after stopping older AML servers. A first optional matplotlib render failed because the package was absent; diagnostics now use existing dependencies plus browser SVG. An initial preservation comparison treated the added AP alias as unequal report structure; comparing each original numerical field confirmed exact metric reproduction. No metric tolerance was relaxed.

## Model results: before and after

| Deployed seed-17 model | Precision | Recall | AP | Threshold | Change |
|---|---:|---:|---:|---:|---|
| GAT | 0.159810 | 0.620499 | 0.210292 | 0.74 | None |
| Logistic | 0.191597 | 0.804247 | 0.200893 | 0.77 | None |

Three-seed GAT mean ± sample SD remains P 0.154474 ± 0.008829, R 0.629732 ± 0.046855, AP 0.233925 ± 0.020622. Logistic is identical across seeds: P 0.191597, R 0.804247, AP 0.200893. Higher mean GAT AP does not erase lower precision/recall or establish significance from three seeds. Evaluation was previously observed, not newly untouched.

Validation GAT F2/F1 threshold 0.74 gives P0.452830/R0.893401, FP638/FN63; F0.5 threshold0.89 gives P0.669355/R0.421320, FP123/FN342. Calibration Brier improves on the internal later-validation partition, but that period already influenced checkpoint choice. Raw scores remain model scores. Removing explicit edges at fixed weights changes validation AP0.542773→0.492678; no causal or retrained-ablation claim.

## Demo and performance

Current canonical **ZEN-e5a3fceee610 / transaction106776627**: five nodes/five edges, score0.964630,21 evidence records, readiness67/100. Main four transactions remain106776627,218047279,219679769,195439532 in deterministic label-independent order. UUIDs change per new instance. Historical canonical ZEN-e0fbc40247b5 is unchanged.

Final source-check profile on the same historical canonical: median0.447428s before vs0.000949s with cached index across seven checks; one-time index construction0.242764s. Outputs identical. This excludes graph ingestion and is not an end-to-end throughput claim. Local narrative generation remains a substantial stage cost; single-process CPU and memory limits remain.

## Remaining limitations and next best step

Low minority precision, anonymous features, small seed study, reused evaluation set, constrained prose, no genuine identity/reference data, bounded explanation size, no prospective calibration or production workload/security validation. Local audit hashes have no independent immutable anchor. SubgraphX, GAT-specific SHAP, live reference adapters, per-stage human approvals, distributed/federated operation, fiat adaptation and filing remain deferred/adapted/future as explicitly mapped in docs/IMPLEMENTATION_DECISIONS.md.

The most valuable next step is obtaining an authorized, genuinely new evaluation population and predeclaring operating-point/calibration assessment before inspecting its outcomes. Current enhancements make the capstone clearer and more defensible; they do not improve deployed detection accuracy.

## Evidence and handoff

Start `./scripts/start.ps1 -Port 8002 -NarrativeProvider local`; see docs/CAPSTONE_DEMO.md for literal navigation and synthetic review setup. Final runtime uses http://127.0.0.1:8002. Review docs/VALIDATION.md, docs/MODEL_CARD.md, docs/SYSTEM_CARD.md, docs/EVALUATION.md and docs/IMPLEMENTATION_DECISIONS.md. The live case database retains every case and its full review/audit history.
