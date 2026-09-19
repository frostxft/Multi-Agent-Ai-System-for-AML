# Proposal-to-implementation decisions

The master specification remains the original scope reference. These are explicit implementation decisions and limits, not removals of the project objectives.

| Proposal concept | Implementation and trade-off |
|---|---|
| Accounts as nodes, transactions as edges | Elliptic actually contains transaction nodes and directed payment-flow edges. Preserve its real semantics. No fabricated account identities. A future account-feed adapter remains necessary. |
| GAT / network detection | Real two-layer PyG GAT with 2 attention heads, hidden width 16, weighted binary loss. Cases are incoming two-hop computational neighborhoods around scored transactions, not separately supervised ring classifications. |
| GNNExplainer / SubgraphX | GNNExplainer implemented and exercised. SubgraphX deferred because one working graph attribution method suffices for this slice. Masks include a top-edge deletion intervention; negative/weak fidelity is surfaced. |
| SHAP-validated compliance | SHAP LinearExplainer explains the independent logistic baseline in log-odds and checks additivity. SHAP cannot validate narrative truth or legal compliance. Dedicated evidence consistency checks supply that limited control. |
| Five agents | Five concrete components coordinated sequentially, each with separate inputs, outputs and responsibilities. Persistent per-stage input/output hashes, snapshots, timings and errors provide execution traces. No agent framework dependency or distributed messaging. |
| RAG | Case-scoped TF-IDF retrieval over structured evidence, then evidence-linked narrative assembly and configurable generation. This small corpus does not need a vector database. |
| LLM | Explicit extractive mode is runnable without a download or paid API. Local FLAN-T5 constrained generation and Ollama free-text providers are implemented. Their actual verification state belongs in PROJECT_STATUS.md. Failures never silently fall back. Local generation is restricted to combinations of retrieved facts; linguistic freedom is intentionally limited. |
| KYC and sanctions | No authentic identity/KYC or sanctions reference is present. Dossiers explicitly return unavailable. No genuine profiles or matches are invented. Typed protocols and explicitly synthetic snapshot fixtures now exercise the boundary; real adapters/authorized reference feeds remain future work. |
| Compliance and readiness | Exact cited-fact consistency, required disclosures, evidence association, model-score match and explanation checks. Conservative scorecard with six equal-weight checks; stale benchmark and missing identity context remain false. Human-only disposition regardless of score. Not legal certification or a regulatory scoring standard. |
| Persistence / orchestration | SQLite case snapshots and hash-linked audit events. Optional Fernet payload encryption; plaintext IDs/revisions still visible. No administrator-proof immutable log or external integrity anchor. |
| RBAC / encryption in transit | Configurable analyst/reviewer bearer roles, loopback-only unauthenticated demo mode, same-origin mutation checks, CSP and no-store responses. HTTPS available through Uvicorn TLS settings; TLS and key-management maturity must not be assumed from local HTTP operation. |
| Investigator UI | Same-origin HTML/CSS/JavaScript served by FastAPI avoids a separate frontend build/runtime. Real API state, pan/zoom graph, attributions, evidence, dossiers, draft editing, validation, review and audit. Graph viewport caps at 70 displayed nodes; stored case neighborhood is intact. |
| Scalability | Single process, CPU model; explanation refuses neighborhoods over 1,500 nodes and persists a failure. Multiworker/distributed scaling, large-neighborhood explanation and incremental transaction feeds remain future work. |

## Evaluation policy

Train time steps 1–29; validation 30–34; test 35–49. Unknown labels can contribute graph context but never supervised loss or evaluation targets. Normalize using only training-period nodes. Exclude time and the 72 pre-aggregated neighbor features; use 93 local anonymized features for both models. Edges are filtered at split cutoff, and inference at the target's time step. Best epoch by validation average precision; threshold selected by validation F2. No test-set tuning or labels in investigative evidence. The preserved first run is one seeded CPU experiment. A fixed three-seed replication is now separately reported in EVALUATION.md and multiseed_evaluation.json; the previously observed test period is reused, not newly untouched. Precision-recall area is reported using sklearn average precision, not trapezoidal integration.

The dataset's local features can themselves summarize transaction inputs/outputs. “Tabular baseline” means no explicit message passing, not absence of all relational information. Full time-step snapshots support retrospective analysis, not an intrastep real-time guarantee.

## Original proposal assumptions preserved

The original 12-week plan remains: weeks 1–4 detection/triage, weeks 5–8 investigation/narrative and four cases, weeks 9–12 compliance/governance. The team allocation remains a planning reference in the master specification. Near-zero setup, INR 2,000–5,000 development cost, 300 total hours / 75 per member, possible GPU/API costs, 90% baseline false positives, 30% reduction, 10,000 alerts/month and 2,700 fewer alerts/month are proposal illustrations. None is a measured achievement or actual cost record here.

Fiat adaptation, drift monitoring, cross-institutional/federated privacy-preserving operation and extensions to insurance fraud, fintech mule networks, telecom SIM fraud and e-commerce payment fraud remain future directions. No unrelated industry functionality is implemented.

GDPR, GLBA, India's DPDP Act and SR 26-2 are proposal references, not certifications or verified legal interpretations by this prototype. The specification's fines and market claims are not independently endorsed here. No legal requirement is declared satisfied.

## Primary technical sources

- [Elliptic paper, graph/feature semantics](https://arxiv.org/html/1908.02591v1)
- [Elliptic publisher dataset](https://www.kaggle.com/datasets/ellipticco/elliptic-data-set)
- [PyG Elliptic implementation](https://pytorch-geometric.readthedocs.io/en/latest/_modules/torch_geometric/datasets/elliptic.html)
- [PyG GATConv](https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.nn.conv.GATConv.html)
- [PyG GNNExplainer](https://pytorch-geometric.readthedocs.io/en/latest/generated/torch_geometric.explain.algorithm.GNNExplainer.html)
- [Google FLAN-T5-small model card](https://huggingface.co/google/flan-t5-small)


## Proposal alignment audit — updated 2026-09-15

| Major capability | Status | Actual implementation / boundary |
|---|---|---|
| Python / open-source stack | Implemented | Python, PyTorch/PyG, sklearn, SHAP, Transformers, FastAPI, SQLite and browser assets; no paid service required for local demo. Dependency lockfile retained. No independently completed license audit claimed. |
| GNN/GAT | Implemented | Real supervised transaction-node GAT and logistic comparator, original run plus fixed three-seed replication. Detection quality remains modest. |
| Network/ring detection | Intentionally adapted | Connected incoming computational neighborhoods assembled as cases. No ring labels or separately supervised ring classifier. |
| GNNExplainer | Implemented | Optimized node-feature/edge masks, score reproduction check, ranked presentation, deletion sensitivity and limitations. No confidence calibration or causal claim. |
| SHAP | Intentionally adapted | Exact linear baseline attribution in log-odds with additivity check; not GAT attribution or narrative validation. |
| SubgraphX | Deferred | Not implemented; no placeholder output. Decision below. |
| Rule/ML triage | Implemented | GAT score plus configurable priority thresholds and visible rationale; no validated typology rule engine. |
| RAG | Implemented | Case-scoped TF-IDF retrieval over actual evidence. Not an external knowledge base or vector search platform. |
| LLM | Partially implemented | Real local FLAN-T5 constrained fact-pair selection verified; free paraphrase unproven, Ollama adapter unverified. Default deterministic extraction is labeled distinctly. |
| KYC | Adapted / improved boundary | Typed provider and synthetic snapshot profile adapter with explicit fixture entity linkage and source/version; benchmark remains unavailable. Genuine profiles and entity resolution are future work. |
| Sanctions | Adapted / improved boundary | Typed provider, versioned synthetic static snapshot and exact-ID fixture matching only. No genuine sanctions feed/list ingestion, fuzzy screening or live service; benchmark unavailable disclosure retained. |
| Five agents | Implemented | Detection, triage, investigation, narrative, compliance are concrete modules with real outputs and visible failures. |
| Orchestration | Implemented | Sequential resumable pipeline, typed handoffs, per-stage persistence and timing; no distributed agent framework. |
| Graph-to-text | Implemented | Source transaction/edge records become case-scoped evidence facts, dossiers and cited draft claims. Model/derived output stays separately labeled. |
| Human oversight | Partially implemented | Mandatory final review, revisions, notes, role checks, locked final states; intermediate outputs inspectable, but separate human approvals at every stage are not enforced. |
| Governance/consistency | Implemented within prototype scope | Source rechecks, exact claim validation, mandatory scope disclosures, contradictions/model mismatch, approval blocking and auditable revisions. No legal/regulatory certification. |
| Readiness scorecard | Intentionally adapted | Internal six-factor equal-weight score, reasons/weights exposed; required human review is outside the denominator. Score cannot authorize filing. |
| API handoffs | Partially implemented | FastAPI lifecycle endpoints and in-process agent contracts. External banking feeds, independent per-agent network APIs and regulatory filing integration remain future work. |
| Security controls | Partially implemented | Default loopback, origin/host checks, CSP/no-store/escaping; optional tested bearer roles, payload encryption and TLS. No enterprise identity/key management or trusted external audit anchor. |
| Scalability direction | Future work | Single-process CPU demonstration; 1,500-node explanation bound and 70-node UI viewport. No production load, federation, fiat adaptation or drift validation. |

## Explainability investigation

SHAP's model-agnostic interface requires a defined masking/background policy ([official SHAP documentation](https://shap.readthedocs.io/en/latest/generated/shap.Explainer.html)). One could hold topology and neighboring features fixed and perturb the target's 93 features, but that would answer only a conditional target-feature question, not explain the whole network. Perturbing anonymous correlated features can produce unrealistic inputs; a graph coalition/background policy and stability budget have not been validated here. We therefore choose the permitted baseline-only option. This is not a claim that GAT-compatible SHAP is impossible. No surrogate or GAT SHAP has been implemented or represented as validated.

[SubgraphX](https://proceedings.mlr.press/v139/yuan21c.html) searches subgraphs with Monte Carlo tree search and Shapley-based importance. Reliable integration would require a target-preserving node-classification objective, coalition semantics, runtime bounds and comparative stability/fidelity tests. Those are not supplied by merely wrapping existing GNNExplainer masks. Given a working explanation path and modest detector quality, this build prioritizes transparent attribution and source-grounding checks. SubgraphX remains explicitly deferred, not installed or experimentally validated, and no claim of environment incompatibility is made.

## KYC/sanctions decision — enhancement

Typed provider protocols and a deterministic synthetic snapshot adapter now exercise the interface. Only explicit synthetic transaction/entity linkage is accepted; benchmark configuration rejects fixtures. Source/version and labels are visible, supplemental fixture context stays outside benchmark/LLM evidence and does not satisfy genuine-identity readiness. A real static sanctions provider, authorized live feed, entity resolution and match-quality validation remain future work.

## Claim audit

Repository Markdown was searched for production-ready, regulatory compliant, high accuracy, 90% false positives, 30% reduction, ROI, real KYC/sanctions, live banking, guaranteed and proven. Matches in the unchanged master specification are attributed proposal assumptions/illustrations (including its feasibility language and legal references); README/status/decision records qualify benchmark, prototype and unverified claims. No such numerical business claim is promoted as an achieved result. Detailed match output is retained in artifacts/claim-audit.txt. The master specification remains the proposal baseline.

## Enhancement alignment and design choices

Detection evaluation is **improved** with validation-only operating points, calibration diagnostics and fixed-weight topology intervention; deployed training remains unchanged. Network case construction is **improved/adapted** with local structure and per-neighbor scores, not a supervised ring detector. Dossier, temporal source navigation, evidence retrieval, draft revision comparison, compliance checklist, case comparison/filtering, audit provenance and status/model inspection are **implemented/improved**. A single default workstation serves investigators and evaluators; no duplicate demo mode was needed.

Typed synthetic reference adapters are **adapted** proposal coverage, not real KYC/sanctions. Original GNNExplainer, separate baseline SHAP, sequential five agents, mandatory final review, source-grounded drafting and audit remain implemented within their existing limits. SubgraphX, GAT-specific SHAP, free narrative generation, separate approval at each agent, independent distributed agent APIs, real identity data, legal filing and production infrastructure retain the explicit deferred/future statuses above. No major requirement was silently removed.

Source validation now builds an ID/edge index once per loaded graph; overview reuses its verified profile and SQL count rather than rescanning the dataset. No distributed cache or new database dependency. Evidence checks retain the same source semantics; the profile compares outputs against the preserved implementation on the same canonical case. Case list pagination remains future work for larger stores.
