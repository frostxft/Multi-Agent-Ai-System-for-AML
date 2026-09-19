# Judge / investigator UX decisions

## Verification status — 2026-09-17

The milestone is complete. The four-case manifest loaded in Judge Mode, the canonical case opened from Start investigation, and the full investigator journey was exercised in the browser. Evidence E0006 was followed from its source record to the linked transaction in the network. Technical Mode exposed the retained 20-case history, benchmark metrics, threshold explorer, calibration caveat, topology diagnostic, and provenance. The narrow viewport check showed no document-wide overflow. No browser console errors were observed in the checked flows. This is workflow verification, not an independent usability study.

## Purpose

The final presentation release makes the existing investigation understandable before exposing implementation detail. No trained detector, pipeline output, source fact, threshold, benchmark metric or historical case is changed. Judge Mode is the default, with Technical Mode available beside it. The design goal is a 30-second guided understanding; automated inspection is not a measured usability study with independent judges.

## What appears first

The landing screen explains the product, displays Detect → Explain → Investigate → Report → Validate → Review → Audit, and opens the existing canonical case through Start investigation. The operational cards count only the visibly named collection: pending human reviews, high-priority open cases, explicitly traceable evidence, and ready/blocked reviews. They are persisted prototype cases, not live-bank workload or production throughput. Evidence-ready requires the backend evidence_traceable check and actual records; missing validation never becomes ready by default.

The case overview answers what a case is, why it was flagged, which source fact supports it, what text the system prepared, and who decides. Concise reasons are deterministic presentation functions of actual scores, case thresholds, connected-node/edge counts and available explanation masks. They do not call anonymous features amounts, velocity or typologies. Missing outputs render pending, and below-threshold scores render below-threshold wording.

## Collection and history

Judge Mode follows the ordered IDs in artifacts/benchmark/demo_manifest.json. Its current canonical remains ZEN-e5a3fceee610 / transaction 106776627. A read-only authenticated collection endpoint validates model/dataset identity and transaction associations. Missing or mismatching collections fail closed with an explanation; users can still inspect all runs in Technical Mode. No label-based selection, new ranking, history deletion or silent replacement of the canonical case occurs. Technical Mode includes repeated historical runs and their real timestamps/revisions. Switching presentation never edits case state.

## Progressive disclosure

Necessary context is visible: reason, model-score caveat, source facts, explanation relationships, status/findings and human oversight. Technical Performance contains dataset statistics, precision/recall/AP, original and three-seed evaluation, threshold exploration, calibration, topology intervention and provenance. Graph filters and structural statistics sit under Explore the network and Network analytics. Timing, hashes, raw JSON and source/version details are expandable. Technical Mode opens the deeper explanation/readiness controls and preserves all historical runs.

Explanation starts with plain reasons, a network preview, ranked relationships and accessible links to the interactive graph. Raw features move under Technical explanation / Technical feature attribution because their real-world semantic meaning is unavailable. Displaying Feature 55 rather than local_feature_55 changes only the label, not its value or meaning. Full raw masks are retained. SHAP has its own disclosure, explicitly explaining the independent logistic baseline rather than the GAT.

## Semantics and evidence

Elliptic nodes are transactions; edges are directed payment flow between transactions. No node is described as an account/customer. Dataset time steps are not calendar timestamps. Model scores are not calibrated probabilities of money laundering. Explanation weights are relative attributions, not measured confidence or causal/legal evidence. Rank numbers avoid inventing universal strong/moderate mask cutoffs.

Evidence cards retain exact facts, records and versions. FACT, MODEL OUTPUT, DERIVED ANALYSIS, GENERATED TEXT, EXTRACTED TEXT, INVESTIGATOR NOTE, MISSING CONTEXT and SYNTHETIC DEMO DATA distinguish origins. Source facts have source/provenance disclosures and transaction-to-network navigation; anonymous attributes remain available from node inspection. Derived/model statements remain explicitly labeled, not promoted into source facts. Draft claims keep clickable citations and unsupported claims are visually highlighted.

## Generation and review

The provider label distinguishes deterministic extraction, constrained local model summary and configured Ollama. Dossier/report/overview never describe extracted text as free LLM prose. Readiness leads with Ready for human review, Blocked, Awaiting validation, Changes requested or the actual final decision. The numerical Internal Prototype Readiness Score and factors are secondary and never authorize filing.

The reviewer sees AI prepares the case; a human investigator makes the decision before the action controls. Notes, revision checks, reviewer permissions, unsupported-claim blocking and final-state locking are unchanged. Audit labels translate actual completed/started/failed/reviewer events into a readable timeline; they never synthesize a successful stage from a missing event. Technical event hashes remain inspectable.

## Reference boundary and disclosures

Genuine KYC/sanctions are unavailable in the benchmark. Provider boundaries and source/version details remain inspectable. Existing fixture results retain prominent SYNTHETIC DEMO DATA labels; no synthetic identity enters benchmark evidence. Local demonstration mode is not called production security. Calibration stays NOT DEPLOYED / REUSED VALIDATION DIAGNOSTIC. Fixed-weight graph intervention is sensitivity analysis, not a retrained no-graph baseline or causal proof.

## Accessibility and validation plan

Native buttons, labeled controls, disclosure summaries and visible focus outlines support keyboard use. Selected presentation buttons expose aria-pressed; the current journey step exposes aria-current. Responsive layouts collapse the sidebar/cards, retain internal table/tab scrolling and preserve graph keyboard selection. Full backend tests, pure presentation regression tests and actual browser inspection cover semantics, curated history, pending/blocked states, traceability and technical drill-down. Final observed results are recorded in VALIDATION.md and PROJECT_STATUS.md rather than asserted here in advance.
