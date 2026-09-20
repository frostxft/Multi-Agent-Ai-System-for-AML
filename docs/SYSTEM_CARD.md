# Team Zen system card — 2026-09-15

The system supports a reproducible research investigation of anonymous Bitcoin transactions. It transforms source records and model outputs into inspectable cases and cited drafts, ending with a mandatory investigator disposition. It does not file reports or certify legal compliance.

## Architecture and responsibilities

FastAPI serves a same-origin JavaScript investigator workstation and lifecycle endpoints. A sequential, resumable Python pipeline owns five stages: Detection scores the target with GAT and runs GNNExplainer/baseline SHAP; Triage applies explicit score cutoffs; Investigation records source/model/derived/missing-information evidence, structural context, retrieval and dossier; Narrative emits deterministic claims plus optional constrained local FLAN-T5 summary; Compliance rechecks sources, exact claims, model agreement, disclosures and readiness. SQLite stores each stage snapshot, revisions, reviewer notes and a hash-linked audit chain. Failures persist and can be retried from their stage.

Source CSVs → verified graph/model → target and incoming two-hop neighborhood → case evidence IDs → case-scoped TF-IDF retrieval → cited draft → consistency findings → human disposition → audit. Unknown benchmark labels never become narrative evidence. The full case neighborhood remains stored even when the UI displays at most 70 nodes.

## Investigation improvements

Local degree, fan-in/out, directed density, weak components, cycle presence, path depth, score concentration and dataset-step counts describe only the stored neighborhood. Four derived evidence facts have analyzer-version/data-fingerprint provenance and are recomputed during validation. Scores for neighbors use the graph at the target cutoff, not truncated-neighborhood rescoring. Navigation joins source records, graph nodes/edges, explanations and citations without adding a graph database.

KYC/sanctions protocols accept entity IDs/attributes and return typed source/version results. The unavailable provider is the benchmark default. A deterministic JSON snapshot adapter supports synthetic profiles and exact-ID synthetic matches only with explicit fixture transaction/entity links. Benchmark configuration rejects the synthetic adapter. This does not implement genuine list ingestion, fuzzy entity resolution or live screening. Supplemental fixtures are excluded from benchmark/LLM evidence and do not satisfy genuine-identity readiness.

## Grounding and review

Retrieval enforces one case, unique evidence IDs, exact metadata filters and fact deduplication; it omits zero-similarity results. Similarity is relevance, not fact confidence. Draft claims must exactly match cited facts under the intentionally restrictive policy. Local FLAN-T5 selects a constrained pair of evidence facts; it does not produce unconstrained legally sufficient prose. Extractive, local and explicitly configured Ollama modes are labeled separately; the remote adapter has no live validation claim.

The structured editor exposes supporting facts, unsupported claims, save/revalidation, and historical narrative comparisons. Generation provenance is server-owned; edits record actor, prior hash and revision. Stale revisions and final-state changes are rejected. Reviewer notes and reviewer role are required for disposition. Benchmark demonstration cases have no simulated human decisions; workflow simulations use a separately labeled synthetic database.

Internal Prototype Readiness Score exposes factors/weights/reasons, missing information and blocking consistency findings. It is not a regulatory score. Required human review does not become automated merely because consistency checks pass.

## Governance, security and privacy

Default loopback access, same-origin mutation checks, escaped content, CSP, no-store responses, optional bearer roles, optional Fernet payload encryption and verified TLS are implemented. Status/model routes expose a whitelist rather than tokens, encryption keys or full environment. Trusted local model loading uses torch weights_only; SQL values are parameterized. New source routes require case membership and dataset identity; no ground-truth labels are returned. See SECURITY_PRIVACY_REVIEW.md for inspected scope and limitations.

Audit chains detect inconsistencies using local stored hashes/snapshots; an administrator able to replace the entire database can rewrite history. There is no external immutable anchor or independently authenticated individual identity in loopback mode. Case metadata and artifacts may remain unencrypted even when payload encryption is configured. Real customer data requires separate access, retention, authorization and operational controls. External narrative endpoints are opt-in and transfer evidence only when configured; local/extractive modes require no such service.

## Operating limits and future work

One CPU process, bounded explanations (1,500 nodes), no production load/availability claim. Run training, verification and loaded benchmark servers sequentially on memory-constrained Windows hosts. No new runtime dependency was introduced. Existing requirements-lock.txt remains the environment reproduction reference.

Priorities are a genuinely new evaluation population, prospective calibration/threshold assessment, explanation stability and authorized real entity linkage. SubgraphX, GAT-specific SHAP, live reference feeds, enterprise IAM/key management, regulatory filing, distributed/federated operation and fiat adaptation remain deferred/future capabilities. See IMPLEMENTATION_DECISIONS.md for the full proposal mapping.
