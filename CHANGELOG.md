# Enhancement release — 2026-09-15

- Added validation-only threshold objectives, reliability/calibration diagnostics and fixed-weight topology intervention; preserved deployed model and original benchmark metrics.
- Added versioned local network context, neighbor scores, source inspector, graph filters and evidence navigation.
- Added case-scoped metadata retrieval/deduplication and isolated synthetic KYC/sanctions provider boundaries.
- Added investigator briefing/dossier, structured claim editor and revision comparison, checklist, queue comparison/filters and status/model provenance.
- Hardened bearer parsing, configured URL credential handling and server-owned generation provenance; cached source index/profile; corrected graph mouse selection and responsive overflow.
- Added model/system cards, gap analysis, security/privacy review and evaluator runbook; updated alignment and validation evidence.
- Validation: baseline36 → final46 passing tests; original seed17 metrics reproduced; two four-case local-LLM runs verified; all16 prior cases preserved; all20 main audits valid/no decisions; isolated synthetic edit/block/repair/review/lock verified in browser.
- No new runtime dependency, live external provider, deployed calibration or claim of improved test accuracy.

# Changelog

## 2026-09-19 — Final artifacts & documentation cleanup
- Trimmed `artifacts/` to final runtime/deliverable material only: `benchmark/`, `flan-t5-small/`, `cases.db`, `claim-audit.txt`, `capstone-release-verification/`. Deleted the historical `pre-enhancement-20260915/`, `enhancement-seed17-verified/`, `enhancement-four-case-reproduction/`, `ui-test/`, the three development test logs, `enhancement-preservation-validation.json` and `enhancement-ui-test.db` after confirming no application, test, startup or setup dependency.
- Deleted superseded docs (`docs/ENHANCEMENT_GAP_ANALYSIS.md`, `docs/REPOSITORY_CLEANUP.md`, `docs/FINAL_RELEASE_AUDIT.md`), the stale enhancement validation JSON records, and the obsolete `scripts/verify_enhancement.py`; updated every surviving reference so no documentation points at a removed file.
- Removed the large FLAN-T5 Kaggle source archive `artifacts/flan-t5-small-kaggle.zip` (1.83 GB); the extracted model is complete and reproduced by `scripts/download_llm.py` / `scripts/download_llm_direct.py`. `data/elliptic/elliptic.zip` is retained for `scripts/unpack_data.py`.
- No application code, API, schema, model, evidence, review, audit, UI or SAR-export change. Validation: backend **52 passed**, presentation **8 passed**, `node --check` clean; live app, audit, enrichment, offline FLAN-T5 load, `cases.db` load and SAR-style PDF export verified.

## 2026-09-19 — Final release repository cleanup
- Removed the local virtual environment (`.venv/`, ~1.2 GB) and regenerable Python/test caches (all `__pycache__/`, `*.pyc`/`*.pyo`, `artifacts/new-pytest-run/`, `artifacts/pytest-cache/`). Recreate the environment with `./scripts/setup.ps1` and `requirements-lock.txt`.
- Removed the historical archive `artifacts/archive/` (119 files, 8.5 MB: superseded snapshots, multi-seed reproductions, diagnostics and temporary logs). No application, test, startup or verification script references it.
- Kept every artifact referenced by the application, tests, startup, provisioning or final documentation: `artifacts/benchmark/`, `artifacts/cases.db`, `artifacts/flan-t5-small/`, `data/elliptic/`, the referenced historical verification artifacts (`pre-enhancement-20260915/`, `enhancement-seed17-verified/`, `capstone-release-verification/`, `enhancement-four-case-reproduction/`, `ui-test/` + `enhancement-ui-test.db`), the referenced test logs and validation JSON, and the benchmark source archive `data/elliptic/elliptic.zip`. The root `.pytest_cache/` remains (filesystem-locked; ignored).
- Removed the large FLAN-T5 Kaggle source archive `artifacts/flan-t5-small-kaggle.zip` (1.83 GB) after confirming the extracted weights under `artifacts/flan-t5-small/` are complete, the app loads only that folder at runtime, and `scripts/download_llm.py` / `scripts/download_llm_direct.py` reproduce the model. `scripts/unpack_llm.py` remains and re-downloads the archive first if that path is used.
- No application code, API, schema, model, evidence, review, audit or report-export change. Validation: backend **52 passed**, presentation **8 passed**, `node --check` clean, live API/audit/enrichment validation passed, and the SAR-style PDF export re-verified.

## 2026-09-19 — SAR-style report export: PDF pagination polish
- Fixed an awkward page break where **Provenance / Audit** landed on a page of its own (mostly blank) and the **Technical Provenance & Validation** appendix started on the following page. The appendix now stays with Provenance / Audit (`.pr-tech{break-before:avoid;break-inside:auto}`), so no page contains only a small section — the technical appendix begins right after Provenance / Audit and flows on.
- **Supporting Evidence** now starts on a fresh page (`section:has(.pr-ev){break-before:page}`), matching the intended structure: page 1 title / case information / executive summary / reasons / network context; then supporting evidence; then enrichment / missing information / narrative / compliance / human review / provenance; then the technical appendix (evidence provenance and claim → evidence → source validation).
- Added break hygiene: headings keep with their content (`h2,h3{break-after:avoid}`), table rows are never split (`tr{break-inside:avoid}`), the report header stays with Case Information, and the footer is not orphaned.
- **No content change:** all sections, evidence records, narrative, validation, provenance and both disclaimer lines are unchanged, and traceability is intact.
- Corrected an existing cache-bust gap: `style.css` was still pinned at `?v=27`; `index.html` now references all assets at `?v=30`.
- **Validation:** fresh PDFs regenerated with headless Chrome for two cases; per-page content spans inspected (no near-empty page — the only short page is the natural final tail), and the PDF content/path/disclaimer checks still pass. Backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean.

## 2026-09-19 — SAR-style report export: provenance/professionalism polish
- **Removed personal/local filesystem paths from the exported report.** Benchmark evidence previously rendered raw `C:\Users\...\data\elliptic\raw\*.csv` sources. These are now shown with professional source labels — **"Elliptic benchmark transaction record"** and **"Elliptic benchmark payment-flow record"** — while each record ID and version is preserved (`Workstation.sourceLabel`).
- **Full benchmark fingerprint moved out of the main evidence table.** The Supporting Evidence table now shows a short version reference (e.g. `903ac5dfcaba…`, `Workstation.shortRef`); the Provenance / Audit summary keeps only a short dataset reference. The full model ID, dataset fingerprint and per-evidence versions remain in a new, visually secondary **Technical Provenance & Validation** appendix, which also carries an evidence-provenance table and a claim → evidence → source validation table.
- **No traceability removed:** all evidence IDs, facts, record IDs, versions and provenance relationships are retained, and the exact disclaimers — **"Draft only · Human review required · Not a filed SAR"** and **"Human investigator retains final authority."** — are unchanged. Context, revision, score, threshold, evidence count, time step, findings, synthetic demo enrichment, narrative and compliance/human-review sections all remain.
- Print CSS: added `overflow-wrap:anywhere` / `word-break:break-all` so long identifiers cannot clip, plus subdued `.pr-tech` styling. No backend/model/evidence/schema/API/review/audit change; assets bumped to `?v=29`.
- **Validation:** real PDFs generated with headless Chrome (print-to-pdf) for two cases and text-verified via embedded-ToUnicode extraction — no filesystem paths, all evidence IDs and the full narrative present, sanitized source labels, demo-enrichment and disclaimer text present, full fingerprint only in the technical appendix. Backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean.

## 2026-09-19 — SAR-style report export (print-to-PDF)
- Added an **Export SAR-style Report** button to the SAR Narrative section of the **Evidence & Report** tab. It composes a complete SAR-style investigation report from the currently selected case (case information, executive summary, reasons for review, network/activity context, supporting evidence with provenance, synthetic demo enrichment when present, missing-information/limitations, narrative with citations, compliance/validation, human-review status, provenance/audit) and opens the browser print dialog so it can be saved as PDF.
- Implemented **dependency-free** — no PDF library and no new runtime dependency. The report is rendered into a print-only `#print-report` container with dedicated `@media print` CSS; other content is hidden only while printing, so normal on-screen layout and scrolling are unchanged.
- Every field is derived from the selected case's live API data (case/transaction/evidence IDs, scores, threshold, claims, citations, demo KYC/sanctions, audit); **no case-specific values are hardcoded**. The report is labelled **"Draft only · Human review required · Not a filed SAR"**; approval does not file a SAR. The action performs no review/reopen, so **Review & Audit remains the single human-decision mutation surface**.
- No backend, model, evidence, review, audit, schema, threshold or API-contract change.
- Validation: backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean; report output verified case-dynamic across two cases (no cross-case leakage, no truncation of evidence or narrative); served assets confirmed at `?v=28`.

## 2026-09-19 — Judge Mode scrolling/layout correction
- Made the page the single vertical scroll surface: removed the desktop case-queue nested scroll (`position:sticky` + `max-height: calc(100vh - 24px)` + `overflow-y:auto`), so the queue flows with the page and no longer captures the mouse wheel.
- Reduced sticky occlusion: the case header now scrolls normally and only the tab navigation (`.steps`) is sticky, so section headings, graph nodes, evidence records, report paragraphs and buttons are no longer hidden behind a tall sticky header. Added `scroll-padding-top` so in-page scroll targets clear the sticky nav.
- Guaranteed content can grow: `.detail`, `#tab-body` explicitly `height:auto; max-height:none; overflow:visible`; the network graph is `display:block; width:100%; height:auto; max-width:100%` so it is never clipped.
- No functional change: APIs, schemas, case/evidence/audit data and the four workspace tabs are unchanged. Validation: backend **52 passed** (3 warnings), presentation **8 passed**, `node --check` clean.

## 2026-09-19 — Final Judge UX Polish & Repository Cleanup
### UI
- Standardized EOI stage terminology across the judge-facing UI: **Detection → Risk Triage → Investigation → SAR Narrative → Compliance → Human Review → Audit**; the four-tab **case workspace** (Overview / Network & Explanation / Evidence & Report / Review & Audit) is now the sidebar navigation, clearly distinct from the workflow stages.
- Removed the inconsistent sidebar labels ("Explainability", "Validation & Review"); explainability is no longer presented as an independent stage (GNNExplainer sits inside Detection; SHAP is the Compliance baseline cross-check).
- Reduced technical terminology in Judge Mode: "Transaction network · AI detection" (was "Transaction graph · GAT"), "What influenced this case" (was "Model explanation"), "Transaction network — connected payment-flow context" (was "transaction-node prediction"), "Detection model" in the cross-check labels (was "GAT"), and "detection-model input" (was "GAT model input"). Network & Explanation opens with "Why did ZEN focus here?" and keeps "Explanation relevance" and "Explanation weight, not confidence or proof."
- Compliance section now reads "ZEN validates the investigation, evidence traceability, report grounding and model provenance before human review." SAR terminology standardized ("SAR Narrative", "SAR-style draft", "Approval does not file a SAR.").
### Repository
- Removed only verified generated/temporary/obsolete files: `aml/__pycache__/`, `scripts/__pycache__/`, `tests/__pycache__/`, `artifacts/release-server.log`, `artifacts/release-server-error.log`, `artifacts/final-consistency-verification/`. The empty root `.pytest_cache/` could not be removed (filesystem lock) and remains gitignored.
- Preserved all required source, tests, documentation, model/data artifacts, demo/deployment files, cases database and audit history. No case/review/audit data deleted.
### Verification
- Backend **52 passed** (3 upstream warnings); presentation **8 passed**; `node --check` clean on all four web scripts. Application started from the cleaned repository; API smoke (20 cases, canonical collection, overview 203,769/234,355, demo enrichment, valid audit) and multi-case dynamic render passed. Technical Mode retains GAT/GNNExplainer/SHAP/model ID/fingerprint/metrics/provenance.

## 2026-09-19 — Remove duplicate Human Review from Evidence & Report
- Removed the duplicate human-decision controls (investigator notes, Approve, Request changes, Reject) from the Evidence & Report tab; the report now shows a compact, dynamically-generated review-status summary ("Human review required / Awaiting human review", "Human review completed / Approved|Rejected", "Changes requested / Returned for investigator updates") with a **Review & Audit →** CTA that switches to the Review & Audit tab for the current case (no reload, no mutation).
- **Review & Audit is now the single mutation surface for human decisions** (Approve / Request changes / Reject / Reopen for review). Removed the duplicate `data-report-decision` `/review` POST from the report; the only review/reopen calls are in `judge.js`.
- Preserved approval/reopen/revision/audit behavior; no governance logic changed.
- Live lifecycle verified: approve → Evidence & Report "Approved"; reopen → new revision, "Awaiting human review"; prior approval retained in the review list and audit chain.
- P2 findings: (a) `ZEN-5acf0e22710a` was already returned to `awaiting_review` via the legitimate reopen workflow (rev 17) with all historical decisions preserved; (b) the list endpoint field is `readiness` (67) — a `readiness_score` alias now exposes the same canonical value (no validation logic changed); (c) the `torch.jit.script` FutureWarning originates from PyTorch Geometric (upstream), not this code — model untouched, warning documented.
- Validation: backend **52 passed**, presentation **8 passed**, `node --check` clean.

## 2026-09-19 — EOI Alignment & Judge UX Pass
- Aligned the judge-facing workflow to the seven EOI stages: **Detection → Risk Triage → Investigation → SAR Narrative → Compliance → Human Review → Audit**, mapping existing technical components inside each stage (GAT + GNNExplainer under Detection; thresholds/network signals under Risk Triage; evidence retrieval + RAG dossier + demo KYC/sanctions under Investigation; local draft under SAR Narrative; validation/provenance/SHAP baseline cross-check under Compliance; approve/request changes/reject/reopen under Human Review; hash-linked trail under Audit).
- Reworked the "How ZEN works" flow and the System Architecture view to the EOI stages, with an explicit Explainability layer (GNNExplainer = local GAT explanation; SHAP = independent logistic-baseline cross-check, **not** the GAT) and a **Future work (not implemented)** note (live KYC, live sanctions screening, SubgraphX explainability, calibrated probabilities, production bank integration, prospective evaluation, demonstrated false-positive reduction, identity resolution, drift monitoring, federated deployment, automatic disposition).
- Judge UX/terminology: renamed "Draft report" to **SAR narrative** (draft · human review required · not a filed SAR); friendly status label **Awaiting human review** (and Changes requested/Approved/Rejected) for case cards and the case header. Judge Mode keeps progressive disclosure; all GNN/RAG/SHAP/GNNExplainer/FLAN-T5/model-ID/fingerprint/feature-ID/API detail remains available in Technical Mode.
- Confirmed all case-specific content (case/transaction/evidence IDs, scores, counts, network relationships, KYC/sanctions demo values, claims, report text) is dynamically derived from the selected case; no hardcoded case IDs, transaction IDs, evidence IDs, counts, KYC or sanctions values exist in the frontend.
- SubgraphX verified **not implemented** in the repository (GNNExplainer supplies graph attribution); labelled future-work rather than faked.
- Validation: backend **52 passed**, presentation **6 passed**, `node --check` clean; multi-case dynamic rendering verified (distinct per-case signatures). No model, dataset, evidence, provenance, schema, threshold or API contract changed. No false claims of live KYC/sanctions, filed SAR, ROI or measured false-positive reduction.

## 2026-09-18 — Capstone PPT alignment: demo KYC / sanctions enrichment
- Added an isolated, clearly-labelled synthetic demo enrichment layer (`aml/demo_enrichment.py`) exposed read-only at `GET /api/cases/{id}/demo-enrichment`. Values are deterministic per transaction, never a GAT input, and never written into benchmark evidence or provenance.
- Judge Mode now shows an "Investigation enrichment" panel (demo KYC profile + demo sanctions screening with result, reference, timestamp and match status); validation gains demo KYC/sanctions availability rows; the report is labelled a SAR-style draft and gains a demo-enrichment section. Architecture view and workflow updated to Detect → Triage → Investigate → Report → Validate → Human review → Audit.
- Validation: 50 backend + 6 presentation tests passed; GAT, dataset, evidence and provenance unchanged.
- Consistency pass: Overview and the report now render the same demo-enrichment component; the report's KYC/sanctions "unavailable" claims are qualified as genuine/live-only where the synthetic demo layer is shown; the "How ZEN works" workflow is a single horizontal row of the seven stages on desktop.
- Full Judge Mode consistency sweep: demo KYC/sanctions enrichment now rendered on Overview, Network & Explanation, Evidence & Report (report + evidence rows) and Review & Audit; a shared `Judge.qualify()` presents genuine-reference "unavailable" statements as "Genuine/Live … only" wherever the synthetic demo layer is present (report claims, evidence cards, report evidence rows); the case header and case queue are labelled. Checked programmatically across all 20 stored cases; no unqualified contradiction remains in judge-facing text.
- Evidence & Report: added a compact, case-dynamic "Transaction snapshot" (transaction ID, model score, alert threshold, connected transactions, evidence records, dataset time step) with an "Investigation context" sentence before "What supports this case"; the "View all N evidence records →" button now clears the search filter, re-renders the full evidence list and scrolls to it. Works for every case; no backend/evidence change.
- Validation: replaced the raw checklist with a judge-friendly "Validation status" summary (Explanation available · Evidence traceable · Report validated · Model provenance recorded · Benchmark limitations · Human review required) plus an explicit genuine-vs-synthetic identity/sanctions distinction; all raw readiness checks, weights, score and JSON moved under a collapsed "Technical validation details". Validation logic, scores and backend unchanged.
- Human review UX: a case with a recorded decision now shows a clear "Decision recorded" state explaining that review actions are locked (a decided case cannot be silently reopened), while genuinely awaiting/changes-requested cases show all three actions with required investigator notes and a clear client-side message for notes under three non-whitespace characters. Existing decision history is preserved; review/audit schemas unchanged.
- Added a controlled "Reopen for review" mechanism: `POST /api/cases/{id}/reopen` (reviewer only, requires a reason and matching revision) moves an approved/rejected case back to `awaiting_review` in a new revision. The previous decisions stay in the append-only review/audit history; the reopen event records the reason, source status and preserved decisions. Frontend shows a "Reopen for review" action with a required reason for decided cases; after reopening the three review actions are enabled. Covered by two new tests (full flow + guardrail).

## 2026-09-17 — Judge experience verification complete
- Verified the deterministic four-case Judge collection and preserved all 20 historical technical runs.
- Verified the complete browser journey from dashboard through audit, including evidence-to-source-to-network navigation and technical disclosures.
- Validation: 48 backend tests and 5 presentation tests passed; no browser console errors in the checked flows.

## 2026-09-18 — Final Judge/Demo re-verification
- Re-inspected the repository against the master specification and re-ran the full test suite rather than trusting the status file: 48 backend + 5 presentation tests passed; `node --check` clean on all web scripts.
- Runtime API verification against the real Elliptic graph and checkpoint confirmed the canonical demo collection, four-case manifest order, 20 preserved runs, canonical transaction/score/evidence, valid audit chain and zero review decisions.
- Held-out and three-seed metrics re-read from artifacts and match the recorded values exactly. No code, artifact, dependency or data was changed.

## 2026-09-18 — UI/UX redesign — Judge workspace
- Redesigned the frontend presentation/layout/styling only: four-step Judge Mode workflow (Overview → Network & Explanation → Evidence & Report → Review & Audit), compact investigator queue, sticky case header, visual "why flagged" bullets, stage timeline, legended interactive network, scannable evidence cards, report-styled draft, prominent human-review panel, and chronological audit timeline.
- Moved GNNExplainer/SHAP/calibration/multi-seed/provenance/raw JSON behind progressive disclosures and Technical Mode. Model scores shown as decimals; scores never labeled probabilities; anonymized features remain labeled.
- Updated `tests/ui_presentation.test.cjs` wording to match the rewritten `reasons()` text (same intent). No backend, model, metric, threshold, data or schema change.
- Validation: 48 backend + 5 presentation tests passed; `node --check` clean on all four web scripts; four canonical cases still resolve on the live server.

## 2026-09-18 — Final release audit
- Ran the complete suite (48 backend + 5 presentation tests; `node --check` clean) and started the application with the canonical command, exercising the real HTTP endpoints at `http://127.0.0.1:8002`.
- Verified Judge Mode default, four-case demo collection in manifest order, canonical case/transaction/metrics, evidence traceability, human-review (zero decisions), audit integrity, and documentation consistency.
- Restored `artifacts/claim-audit.txt` (referenced by `docs/IMPLEMENTATION_DECISIONS.md`) to its documented location.
- Recorded the audit in the project status record. Repository frozen for the capstone: no model, threshold, metric, case-selection, evidence, schema, or presentation changes.

## 2026-09-18 — Final repository cleanup
- Removed regenerable development clutter (23 paths): Python `__pycache__`, pytest basetemp/cache directories, and an empty `hf_cache`. No source, data, model or evidence was removed.
- Archived historical snapshots/reproductions/diagnostics, historical reports, a superseded synthetic test database, and 48 temporary logs to `artifacts/archive/`.
- Preserved all benchmark data, the GAT checkpoint/evaluation/manifests, the 20-case database, the local FLAN-T5 model, both large source archives, and every artifact referenced by docs/code.
- Standardized the canonical demo to `./scripts/start.ps1 -Port 8002 -NarrativeProvider local` → `http://127.0.0.1:8002`; extended `.gitignore`.
- Validation: 48 backend + 5 presentation tests passed; `node --check` clean; runtime demo verification unchanged (canonical four cases, valid audits, zero decisions).

## 2026-09-13 — Implementation started
- Inspected the empty implementation repository and authoritative specification.
- Created the engineering truth document before coding.
- Validation: filesystem and specification inspected; no implemented functionality claimed.

## 2026-09-13 — Real benchmark model and case pipeline
- Acquired/inspected real Elliptic data; preserved actual graph semantics and source hashes.
- Built weighted PyG GAT, temporal evaluation, logistic baseline, GNNExplainer and baseline SHAP.
- Built distinct agent stages, evidence retrieval, dossier/draft validation, persistent review and audits.
- Validation: 25-epoch benchmark run and synthetic lifecycle tests. Held-out GAT AP 0.210292, recall 0.620499; limitations recorded.
- Outcome: real model-derived cases reach awaiting_review without hard-coded scores or fictional evidence.

## 2026-09-13 — Connected network and local LLM demo verified
- Fixed singleton demo selection, requiring connected context without consulting labels.
- Executed four connected extractive cases and four connected local FLAN-T5 cases. Verified mirrored weight checksum against publisher metadata.
- Browser UI uses real APIs; review controls exercised on separate synthetic fixtures.
- Added grounding, temporal isolation, role/host checks, encryption and certificate-verified HTTPS tests.
- Fixed large-file hashing memory failure with streaming hashes/float32 ingestion; full inspection passed.
- Validation: 26 tests passed, actual local LLM generation passed, all benchmark audit chains valid. Accurate README/status and measured JSON reports produced.
- Outcome: integrated prototype with mandatory human review and explicit performance/production limits.


## 2026-09-14 — Capstone evidence and demonstration hardening
- Preserved the original deployed model/report; added fixed seeds 17/29/43 replication, AP terminology, per-seed metrics/sample SD, configuration and runtime/code provenance. Seed 17 reproduced the original metrics; baseline retains stronger precision/recall.
- Enforced declared dataset checksums and source-record revalidation; added exact claim/source trace rows and summary citations, mandatory scope disclosures, readiness factor reasons and whitespace-note rejection.
- Improved model-versus-case wording, ranked graph explanations, clickable evidence, triage rationale and explicit multi-seed comparison in the real-state UI.
- Added deterministic connected-case selection, fail-on-shortfall behavior, canonical manifest and fresh-database/persistence-restart verification.
- Validation: final 36 tests passed (14.52s, 3 upstream warnings); JavaScript syntax passed; real three-seed training, full dataset graph inspection, four local-LLM cases and four independent final recreation cases passed. Browser source navigation, readiness, audit and separate synthetic review/locking verified.
- Outcome: capstone demonstration ready with transparent limits. No newly untouched evaluation population, improved deployed accuracy, KYC/sanctions, GAT SHAP, SubgraphX or production readiness claimed. Updated README/status, evaluator guide, evaluation/verification reports and proposal/claim audits.
