# Team Zen — AML Capstone Master Specification

## Source

This document is a consolidated implementation reference derived from the **Deloitte Capstone 2026 Expression of Interest** for Team Zen, PES University, Bengaluru:

**Use Case Title:** Multi-Agent AI System for Anti-Money Laundering Detection and Reporting  
**Institution:** PES UNIVERSITY  
**Team:** Team Zen

This document preserves the project proposal's stated problem, objectives, assumptions, architecture, technologies, implementation roadmap, governance requirements, scalability direction, market impact, effort/cost assumptions, and ROI illustration.

It is intended to be used as a **project source-of-truth/reference document for implementation**, while the actual implementation may make technically justified refinements.

---

# 1. Project Identity

- **Capstone:** Capstone 2026
- **Use Case:** Multi-Agent AI System for AML Detection and Reporting
- **Team:** Team Zen
- **Institution:** PES University, Bengaluru
- **Proposal Date:** July 05, 2026

## Team Members

1. Manjunatha M — ciferauxaris@gmail.com
2. Manasa H M — manasaprasad12hm@gmail.com
3. Pratham Gupta — prathamg432@gmail.com
4. Tejas P — tejastejasp283@gmail.com

---

# 2. Core Problem

## Problem Statement

The proposal identifies a weakness in legacy AML transaction-monitoring systems:

- They tend to flag transactions individually.
- They can miss multi-account laundering networks.
- Important network-level patterns such as **layering** and **smurfing** may only become visible when transactions are analyzed collectively as a graph.
- The proposal states that these systems can generate **90%+ false positives**.
- Valid alerts can become stuck in slow, manual investigation processes.
- Manual investigation contributes to reporting backlogs.

## Business Implications

The proposal identifies these consequences:

- Increased compliance labour costs.
- Analyst time consumed by false alarms.
- Reduced ability to scale transaction volumes safely.
- Investigation/reporting backlogs.

## Risk if Unsolved

The proposal identifies:

- Alert fatigue.
- Continuing regulatory exposure.
- Enforcement risk.
- It cites FinCEN's **$80M fine for missed SAR filings** and the **$1.3B TD Bank penalty** as examples in the proposal.

Important implementation discipline:
- These proposal figures should be treated as proposal-sourced claims.
- Any use of these figures in final documentation/presentation should be verified against authoritative sources before presenting them as independently verified facts.

---

# 3. Goals and Objectives

The system is intended to:

1. Detect laundering **networks**, not only individual transactions.
2. Automate investigation and reporting activities.
3. Safely reduce false-positive workload.
4. Improve investigator triage speed.
5. Produce audit-ready SAR generation.
6. Support safe scaling of AI autonomy while retaining human oversight.

## Proposed KPIs

The proposal identifies:

1. False-positive reduction from baseline.
2. Faster detection-to-report turnaround.
3. Strong PR-AUC on the minority class.
4. High recall on true laundering cases.
5. Meaningful percentage of alerts safely auto-dispositioned.

The proposal emphasizes that false negatives carry higher regulatory risk, so recall on true laundering should matter strongly.

---

# 4. Complexity

The proposal classifies the use case as **High Complexity**.

The stated reasons are:

- Graph Attention Network / GNN processing.
- Severe class imbalance, stated as **<1% illicit accounts**.
- Five-agent orchestration.
- Hallucination-controlled RAG.
- Evidence grounding.
- Explicit governance framework.

---

# 5. Business and System Requirements

## Business Requirements

The solution is intended to fulfill:

- Suspicious activity detection.
- Alert prioritization.
- Investigation support.
- SAR/STR filing compliance support.

## System Requirements

The proposal requires:

- Explainable AI decisions.
- Auditable AI decisions.
- SHAP-based explainability.
- Regulatory alignment with AI model-risk governance.
- Reference to **SR 26-2** model-risk requirements in the proposal.
- Human oversight at every autonomy stage.

---

# 6. Industry Versatility

The proposal states that the graph-based detection pattern is domain-agnostic.

Potential applications include:

### Insurance
Claims-fraud rings.

### Fintech
Mule-account networks.

### Telecom
SIM-fraud rings.

### E-commerce
Payment-fraud networks.

The proposal's general principle is:

> The graph-based pattern stays similar; node/edge features and reference data change by domain.

---

# 7. Data and Assumptions

## Graph Assumption

Transaction information can be transformed into a graph:

- **Accounts = nodes**
- **Transactions = edges**

## Dataset

The proposal specifies:

- **Elliptic benchmark dataset**
- Public benchmark data.
- Not live banking data.
- Used as a benchmark for the GNN.

## Sanctions

The proposal assumes:

- Static sanctions snapshots rather than live sanctions feeds.

## Human Oversight

The proposal assumes:

- Human-in-the-loop throughout the system.

## Model Domain Limitation

The proposal states:

- The GNN is validated on Bitcoin topology.
- **Fiat adaptation** is future work.
- **Drift monitoring** is future work.

These limitations must remain explicit in implementation documentation.

---

# 8. Proposed End-to-End Solution

The proposal describes the following flow:

**Detection → Triage → Investigation → Narrative → Compliance → Sign-off**

More specifically:

1. **Detection**
   - GNN.
   - Explainability through GNNExplainer/SubgraphX.

2. **Triage**
   - Risk score.

3. **Investigation**
   - RAG dossier.

4. **Narrative**
   - SAR draft.

5. **Compliance**
   - SHAP-validated.

6. **Sign-off**
   - Human review.

## Data Flow

**Transactions → Graph → GNN Score → Triage → Dossier → Narrative → Review**

## Methodology / Resources

The proposal names:

- GNN
- Rule/ML
- RAG
- SHAP
- Transaction data
- Sanctions data
- KYC data
- PyTorch Geometric
- LLM

---

# 9. Architecture

The exact proposal architecture is:

**Transaction Graph → GNN Detection → Risk Triage Agent → Investigation Agent (RAG) → SAR Narrative Agent → Compliance Agent (SHAP) → Human Review**

The architecture is unified under:

- One orchestration layer.
- Graph-to-text bridging.
- Phased human oversight.

## Core Components

### 9.1 Transaction Graph

Represents transaction relationships as a graph.

Conceptually:

- Account/entity → node.
- Transaction → edge.
- Node/edge features provide model inputs.

### 9.2 GNN Detection

Uses graph-based learning to detect suspicious activity at the network level.

The proposal specifically identifies:

- Graph Attention Network (GAT).
- GNN.
- Network-level detection.

### 9.3 Risk Triage Agent

Receives detection results and generates a risk score/priority.

Purpose:

- Prioritize investigator work.
- Focus attention on the most suspicious cases.

### 9.4 Investigation Agent

Uses:

- RAG.
- Supporting transaction/KYC/sanctions information.
- Evidence grounding.

Output:

- Investigation dossier.

### 9.5 SAR Narrative Agent

Uses the investigation dossier to generate:

- SAR draft / narrative.

### 9.6 Compliance Agent

Uses:

- SHAP / explainability.
- Evidence/model consistency.
- Compliance-oriented checks.

### 9.7 Human Review

Final sign-off remains human-controlled.

---

# 10. Graph-to-Text Bridge

A key architectural idea is the bridge between structured graph/model information and LLM-based narrative generation.

Conceptually:

Transaction graph
→ graph model
→ suspicious subgraph / score
→ structured investigation information
→ retrieval/evidence
→ textual dossier
→ SAR draft

The text-generation layer should not replace the underlying graph/model/evidence layers.

---

# 11. Detection Requirements

The detection layer should:

- Work on graph-structured transaction data.
- Detect network patterns.
- Handle severe class imbalance.
- Produce risk/suspicion outputs that can be passed to downstream stages.
- Support explainability.

## Proposed Model

The proposal identifies:

**Graph Attention Network (GAT)**

as the model approach.

## Explainability Options Named in Proposal

- **GNNExplainer**
- **SubgraphX**

## Detection Objective

Move beyond isolated transaction rules and identify coordinated suspicious network behavior.

---

# 12. Triage Requirements

The triage stage must turn raw detection output into actionable risk prioritization.

Expected concept:

**Detection result → Risk score → Investigator priority**

It should help investigators decide:

- Which case should be reviewed first?
- Which alerts are high priority?
- Which cases need further investigation?

---

# 13. Investigation and RAG Requirements

The proposal explicitly calls for:

- RAG (Retrieval-Augmented Generation).
- Hallucination control.
- Evidence grounding.
- Investigation dossier.

The intended principle is:

**Retrieved evidence → grounded investigation → narrative**

The RAG layer should work over available data/reference material such as:

- Transactions.
- KYC.
- Sanctions/reference information.
- Relevant supporting content.

---

# 14. Narrative / SAR Requirements

The Narrative Agent should produce:

- SAR draft.
- Audit-ready reporting support.

The proposal refers to **SAR/STR** filing compliance as part of the business requirement.

The system should clearly distinguish:

- generated draft
- human review
- actual filing

The prototype is intended to support reporting rather than silently file a regulatory report.

---

# 15. Compliance / Explainability Requirements

The proposal requires:

- Explainable decisions.
- Auditable decisions.
- SHAP.
- Human oversight.

The Compliance Agent is positioned after narrative generation and is expected to support:

- Explainability.
- Validation.
- Governance.
- Review readiness.

The proposal specifically describes this stage as:

**Compliance (SHAP-validated)**

---

# 16. Human-in-the-Loop Requirement

Human oversight is central to the proposal.

The proposal states:

- Human-in-the-loop throughout.
- Human oversight at every autonomy stage.
- Final sign-off by a human reviewer.

Therefore the prototype should not be designed as an unbounded autonomous AML decision-maker.

---

# 17. Governance

The proposal calls for an explicit governance framework.

Important principles named or implied:

- Explainability.
- Auditability.
- Human oversight.
- Model-risk governance.
- Evidence grounding.
- Controlled AI autonomy.

The proposal references:

- **SR 26-2** model-risk governance.
- GDPR.
- GLBA.
- India's DPDP Act.

Any production/legal claim should be verified against authoritative sources before final use.

---

# 18. Security and Compliance

The proposal states alignment with:

- GDPR.
- GLBA.
- India's DPDP Act.
- SR 26-2 model-risk requirements.

The stated implementation controls include:

- Human-in-the-loop by default.
- Data encrypted at rest.
- Data encrypted in transit.
- Role-based access control.
- Evidence-grounded narrative generation.
- Explainable AI.

The proposal also connects SHAP to a "right to explanation" concept.

This should be treated as a proposal-level design intention; specific legal interpretations should be independently verified before being presented as legal fact.

---

# 19. Feasibility

The proposal states:

## Technical Feasibility

- GNN is a proven method.
- RAG is a proven method.
- SHAP is a proven explainability method.
- The approach is validated on the Elliptic benchmark dataset.
- No live bank data is needed for the prototype.

## Economic Feasibility

- Open-source stack.
- Near-zero initial cost.

## Integration Feasibility

The solution is intended to:

- Overlay existing case-management/SAR workflows.
- Avoid core system replacement.

---

# 20. Flexibility and Scalability

The proposal identifies a modular five-agent architecture.

Each component can be upgraded independently.

Components that can evolve separately include:

- Detection model.
- Risk rules.
- Reporting logic.

## Scalability Direction

The proposal states that graph-based detection can scale with:

- network size
rather than
- manual rule thresholds.

## Expansion

The proposal describes a potential path toward:

- cross-institutional use.
- federated/privacy-preserving architectures.
- multi-bank deployment.
- industry-wide scale.

These are architectural expansion directions, not necessarily prototype implementation requirements.

---

# 21. Integration Strategy

The proposed system should overlay existing workflows.

The proposal specifically describes:

- Agent-level API handoffs.
- Detection connecting to transaction feeds.
- Narrative output connecting to current SAR workflows.
- Adoption one agent at a time.
- No disruptive rip-and-replace requirement.

## Intended Integration Pattern

Existing transaction feed
→ Detection

Detection
→ downstream case/triage

Investigation
→ evidence/dossier

Narrative
→ existing SAR workflow

Human
→ final review/sign-off

---

# 22. Proposed Technology Stack

The proposal's named tools/technologies are:

## Programming / Orchestration

- **Python**
  - orchestration
  - scoring

## Graph Machine Learning

- **PyTorch Geometric**
  - GNN implementation

## Explainability

- **SHAP**
  - explainability / feature attribution
- **GNNExplainer**
  - graph/subgraph explanation
- **SubgraphX**
  - graph/subgraph explanation

## Generative AI

- **LLM**
  - investigation/narrative generation
- **RAG**
  - evidence retrieval / investigation grounding
- Open LLM/RAG frameworks are intended.

## Data

- **Elliptic dataset**
  - benchmark dataset
- Transaction data.
- KYC data.
- Sanctions data.

## Stack Philosophy

The proposal states:

- Fully open-source approach.
- Public benchmark data.
- No licensed/proprietary datasets.
- Low-cost/near-zero-cost prototype.

---

# 23. Use of Exponential / Emerging Technology

The proposal classifies the system as using emerging technology through:

- Artificial Intelligence.
- Machine Learning.
- Graph Neural Networks.
- Agentic AI orchestration.
- Generative AI.
- Large Language Models.

The core AI concepts are:

**GNN + Agentic AI + Generative AI**

---

# 24. Innovation

The proposal positions the system as challenging traditional rule-based AML scoring.

Three main claimed innovations are:

## 24.1 Network-Level Detection

Instead of only evaluating individual transactions:

- model the transaction network.
- identify coordinated laundering rings.

## 24.2 Evidence-Grounded SAR Generation

Instead of unrestricted LLM generation:

- use retrieved evidence.
- generate reporting narratives grounded in evidence.

## 24.3 Readiness Scorecard / Safe AI Autonomy

The proposal introduces a:

**Readiness Scorecard for safe AI autonomy**

as a way of addressing controlled deployment/autonomy.

These three ideas are described as:

**Three gaps, one system.**

---

# 25. Explicit Proposal Architecture Diagram in Text

The architecture represented by the proposal is:

```text
Transaction Graph
        |
        v
GNN Detection
        |
        v
Risk Triage Agent
        |
        v
Investigation Agent (RAG)
        |
        v
SAR Narrative Agent
        |
        v
Compliance Agent (SHAP)
        |
        v
Human Review
```

Unified through:

```text
Orchestration Layer
+
Graph-to-Text Bridge
+
Phased Human Oversight
```

---

# 26. Proposed Methodology

The proposal explicitly names the following combination:

```text
GNN
+
Rule / ML
+
RAG
+
SHAP
+
LLM
```

These operate over:

```text
Transaction Data
+
KYC Data
+
Sanctions Data
```

with:

```text
PyTorch Geometric
+
Python
+
LLM / RAG pipeline
```

---

# 27. Implementation Roadmap from Proposal

The original proposal defines a 12-week roadmap.

## Phase 1 — Week 1 to Week 4

Focus:

- Detection model.
- Triage.

Milestone:

**Model trained.**

Resources named:

- PyTorch Geometric.
- Benchmark data.

## Phase 2 — Week 5 to Week 8

Focus:

- Investigation Agent.
- Narrative Agent.

Proposal target:

- 4 cases.

Milestone:

**Demo working.**

Resources named:

- LLM.
- RAG.
- Benchmark data.

## Phase 3 — Week 9 to Week 12

Focus:

- Compliance.
- Governance.

Milestone:

**Documentation/demo ready.**

Resources named:

- SHAP.
- LLM.
- Governance/documentation assets.

---

# 28. Proposed Team Responsibilities

The proposal assigns:

## Member 1

- Detection.

## Member 2

- Triage / Investigation.

## Member 3

- Narrative / Compliance.

## Member 4

- Governance / documentation / demo.

These are the original proposed responsibilities and can be adapted during implementation if the team decides to redistribute work.

---

# 29. Proposed Resource List

The proposal names:

- PyTorch Geometric.
- LLM.
- SHAP.
- Benchmark data.
- RAG-based LLM pipeline.
- Python.
- Elliptic dataset.
- Transaction data.
- Sanctions data.
- KYC data.
- GNNExplainer.
- SubgraphX.
- Open LLM/RAG frameworks.

---

# 30. Market Impact

The proposal's expected impacts include:

- Reduced investigator time spent on false positives.
- Faster SAR turnaround.
- Better detection of coordinated laundering networks.
- Direct compliance cost savings.
- Reduced false transaction holds on genuine customers.
- Improved customer experience.
- Improved operational efficiency.

These are intended benefits; a working prototype should not present them as measured production outcomes unless actually measured.

---

# 31. Effort and Cost Assumptions

## Initial Setup

The proposal states:

- Near-zero setup cost.
- Open-source stack.
- Public data.
- No licensing fees.

## Operational Costs

The proposal states that costs may scale with:

- transaction volume.

Potential offset:

- reduced manual investigation hours.

## Hidden Costs

The proposal specifically mentions:

- GPU compute for GNN training.
- Optional paid LLM API calls if not using a local/open-source model.

The proposal estimates:

**INR 2,000–5,000 during development.**

This is a proposal estimate, not a measured current bill.

---

# 32. Effort Model

The proposal estimates:

**300 total hours**

across:

**4 members × 75 hours each**

over:

**12 weeks**

The proposal estimates:

- Phase 1: 100 hours.
- Phase 2: 120 hours.
- Phase 3: 80 hours.

Weekly average:

**6.25 hours/member/week**

---

# 33. ROI Illustration

The proposal provides an illustrative assumption:

- Baseline false-positive rate: 90%.
- Alert volume: 10,000 alerts/month.
- Assumed false-positive reduction: 30%.

Illustrative impact:

**2,700 fewer alerts/month**

The proposal states that this could reduce:

- investigator hours.
- compliance costs.
- fine exposure.

Important:
These values are explicitly an assumption/illustration in the proposal and should not be presented as measured system performance.

---

# 34. Cost Effectiveness Model

The proposal's model is:

```text
Initial:
Near-zero

Operational:
Scales with transaction volume

Potential offset:
Reduced manual investigation

Hidden:
GPU + optional LLM API costs

Development estimate:
INR 2,000–5,000

Effort:
300 hours total
```

---

# 35. Target KPIs — Implementation Interpretation

The proposal's KPI set should translate into measurable engineering outputs.

## KPI 1 — False Positive Reduction

Compare against a declared baseline.

Do not assume the 30% figure from the ROI illustration is achieved.

## KPI 2 — Detection-to-Report Turnaround

Measure actual pipeline time from:

detection
→ triage
→ investigation
→ narrative
→ review-ready case

## KPI 3 — PR-AUC

Measure on the actual benchmark task and report the real value.

## KPI 4 — Recall

Measure true laundering/illicit detection recall.

## KPI 5 — Safe Auto-Disposition

If implemented, measure the percentage of cases meeting the defined safe criteria.

Do not fabricate these figures.

---

# 36. Required Evidence Model for a Strong Working Implementation

Although the proposal describes evidence grounding rather than a detailed schema, a strong implementation should preserve evidence identity throughout the pipeline.

A conceptual evidence record can contain:

```text
Evidence ID
Source
Source Record
Fact
Timestamp / Version where available
Case Association
```

Example:

```text
Evidence ID: E001
Source: Transaction Dataset
Source Record: TX12345
Fact: Entity A transacted with Entity B
```

This supports the proposal's evidence-grounding objective.

---

# 37. Required Distinction Between Data Types

Implementation and documentation should clearly distinguish:

### Benchmark Data
Actual public dataset records.

### Synthetic Test Data
Artificial records created only to test software behavior.

### Model Output
Scores, predictions, embeddings, graph explanations, etc.

### Derived Values
Calculated metrics/risk factors.

### Retrieved Evidence
Records/documents retrieved by the investigation pipeline.

### LLM-Generated Text
Natural-language synthesis based on supplied information.

### Assumption
A project planning or illustrative assumption.

### Human Decision
A decision made by the investigator/reviewer.

---

# 38. Recommended End-to-End Case Object

The exact schema is an implementation decision, but conceptually a case can contain:

```text
Case
├── Case ID
├── Detection Result
│   ├── Risk Score
│   ├── Flagged Nodes
│   ├── Flagged Edges
│   ├── Subgraph
│   └── Model Version
├── Explanation
├── Triage
├── Investigation
│   ├── Evidence
│   ├── Transactions
│   ├── KYC Context
│   └── Sanctions Context
├── SAR Draft
├── Compliance Validation
├── Human Review
└── Audit Trail
```

This is an implementation aid, not a schema explicitly prescribed in the proposal.

---

# 39. Governance / Readiness Concept

The proposal introduces a:

**Readiness Scorecard for safe AI autonomy**

A strong implementation should preserve this concept as a governance/readiness mechanism.

Potential factors can include:

- explanation availability
- evidence completeness
- narrative/evidence consistency
- model confidence
- uncertainty
- human review requirement
- auditability
- data freshness
- model/version traceability

Any final scoring formula should be documented rather than presented as an established regulatory standard unless independently verified.

---

# 40. Scalability Direction

The proposal's long-term direction is:

```text
Single Institution
        ↓
Multi-Institution
        ↓
Cross-Institutional
        ↓
Federated / Privacy-Preserving
        ↓
Industry-Wide
```

This is a future scalability direction rather than a requirement to implement federated learning in the first prototype.

---

# 41. Production-vs-Prototype Boundary

The proposal explicitly assumes:

- benchmark data rather than live bank data.
- static sanctions snapshots.
- human-in-the-loop.
- Bitcoin topology.

Therefore:

### Prototype demonstrates

- network-level graph detection
- orchestration
- investigation support
- RAG
- narrative generation
- explainability
- compliance validation
- human review
- audit trail

### Prototype does NOT automatically prove

- live-bank production readiness
- fiat AML generalization
- live sanctions coverage
- continuous drift monitoring
- regulatory certification
- real-world financial ROI

---

# 42. Implementation Guardrails

The following guardrails are recommended to preserve the intent of the proposal:

## Never fabricate

- model metrics
- transaction details
- sanctions matches
- KYC facts
- model explanations
- regulatory claims
- investigation evidence
- ROI results

## Preserve traceability

A reviewer should be able to move backward:

SAR claim
→ evidence
→ source record
→ transaction/entity
→ graph/model result where applicable.

## Preserve human control

Automation should assist investigation, not silently bypass human review.

## Preserve modularity

The detection model should be replaceable without rewriting the narrative layer.

The narrative model should be replaceable without rewriting the graph model.

---

# 43. Original Proposal Technology Checklist

The complete named technology/tool inventory from the proposal is:

- Python
- PyTorch Geometric
- Graph Neural Networks
- Graph Attention Network
- GNNExplainer
- SubgraphX
- Rule/ML
- RAG
- Retrieval-Augmented Generation
- SHAP
- SHapley Additive exPlanations
- LLM
- Open LLM frameworks
- Open RAG frameworks
- Elliptic benchmark dataset
- Transaction data
- KYC data
- Sanctions data
- Agentic AI orchestration
- Generative AI
- Graph-to-text bridging
- API handoffs
- Role-based access control
- Encryption at rest
- Encryption in transit

The proposal's named regulatory/governance references are:

- GDPR
- GLBA
- India's DPDP Act
- SR 26-2

---

# 44. Original Proposal Architecture / Capability Checklist

A complete implementation aligned with the proposal should account for:

- [ ] Transaction graph
- [ ] Network-level GNN detection
- [ ] Graph Attention Network or justified graph model
- [ ] Class-imbalance handling
- [ ] GNN explanation
- [ ] GNNExplainer and/or SubgraphX
- [ ] Risk triage
- [ ] RAG-based investigation
- [ ] Evidence-grounded dossier
- [ ] KYC context
- [ ] Sanctions context
- [ ] SAR narrative draft
- [ ] SHAP/comparable explainability
- [ ] Compliance validation
- [ ] Human review/sign-off
- [ ] Unified orchestration layer
- [ ] Graph-to-text bridge
- [ ] Auditability
- [ ] Governance/readiness scorecard concept
- [ ] API handoffs / integration posture
- [ ] Modular five-agent architecture
- [ ] Public benchmark data
- [ ] Open-source/low-cost approach

---

# 45. Proposal-to-Implementation Mapping

| Proposal Element | Working-System Interpretation |
|---|---|
| Transaction graph | Build actual graph representation |
| GNN Detection | Train/infer using real benchmark data |
| GAT | Preferred graph model from proposal |
| GNNExplainer/SubgraphX | Explain suspicious subgraphs |
| Risk triage | Produce investigator-priority cases |
| RAG dossier | Retrieve and assemble evidence |
| KYC | Include available/appropriate entity context |
| Sanctions | Use static/reference snapshot if available |
| SAR narrative | Generate draft from dossier |
| SHAP | Explain/validate model factors where technically appropriate |
| Compliance | Validate consistency/readiness |
| Human review | Explicit review/sign-off stage |
| Orchestration | Manage case lifecycle |
| Graph-to-text | Convert graph/model findings into structured narrative inputs |
| Governance | Audit + readiness + human controls |
| Integration | API-level modular handoffs |
| Scalability | Modular components and future cross-institution path |
| Open-source | Prefer open tools/data |
| Elliptic | Benchmark evaluation dataset |

---

# 46. Important Proposal Facts to Preserve in Presentations

The proposal frames the system around the following core message:

> Traditional rule-based scoring can generate large false-positive workloads and can miss coordinated laundering networks.

The proposed answer is:

> Network-level GNN detection + evidence-grounded investigation + SAR generation + governance/readiness controls.

The proposal characterizes the innovation as:

> Three gaps, one system.

Those three gaps are:

1. Network-level detection gap.
2. Evidence-grounded reporting gap.
3. Safe AI-autonomy/governance gap.

---

# 47. Practical Final System Vision

The strongest working interpretation of the proposal is:

```text
                    AML INTELLIGENCE SYSTEM

                 ┌─────────────────────────┐
                 │     Transaction Data     │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   Transaction Graph     │
                 │ Accounts → Nodes        │
                 │ Transactions → Edges    │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │     GNN / GAT           │
                 │ Network Detection       │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │  Graph Explanation      │
                 │ GNNExplainer/SubgraphX  │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   Risk Triage Agent     │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Investigation Agent     │
                 │ RAG + Evidence          │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ SAR Narrative Agent     │
                 │ LLM + Grounded Context  │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Compliance Agent        │
                 │ SHAP + Validation       │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Human Review / Sign-off │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Audit Trail / Governance│
                 └─────────────────────────┘
```

---

# 48. Final Reference Summary

The project is a **high-complexity, graph-based, multi-agent AML prototype** intended to demonstrate:

- detection of suspicious networks,
- investigator triage,
- evidence-grounded investigation,
- SAR-style narrative generation,
- explainability,
- compliance validation,
- human review,
- governance and auditability.

The proposal's named core technology combination is:

**PyTorch Geometric + GNN/GAT + GNNExplainer/SubgraphX + Python + Rule/ML + RAG + LLM + SHAP + Elliptic dataset + Transaction/KYC/Sanctions data.**

The proposed architecture is:

**Transaction Graph → GNN Detection → Risk Triage Agent → Investigation Agent (RAG) → SAR Narrative Agent → Compliance Agent (SHAP) → Human Review**

The proposed implementation roadmap is:

- **Weeks 1–4:** Detection + triage.
- **Weeks 5–8:** Investigation + narrative, with 4 cases as the demo target.
- **Weeks 9–12:** Compliance + governance.

The intended operating principle is:

**Network-level detection + evidence-grounded AI + human-controlled reporting + auditable governance.**

---

# 49. Source Scope Note

This file captures the content of the provided Deloitte proposal and expands some implementation-oriented structure only where explicitly marked as an implementation aid or interpretation.

Where the proposal itself provides a numerical claim, technology, regulatory reference, assumption, cost estimate, roadmap item, or architectural concept, it is preserved here rather than silently replaced.

This document should therefore be treated as the **proposal baseline**, while `PROJECT_STATUS.md` should track what has actually been implemented in the codebase.
