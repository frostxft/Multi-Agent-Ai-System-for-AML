# Focused code, privacy and dependency review — 2026-09-15

Scope: aml/ API, configuration, pipeline, persistence, model/data loading, narrative/retrieval/reference modules; scripts/ download/unpack paths; web/ rendering; existing security tests and new enhancement tests. This is a focused source/test review, not a penetration test, dependency CVE audit, license audit or production certification.

## Concrete changes

- Bearer parsing now requires the Bearer scheme and nonempty ASCII token; a bare token is rejected. Comparison uses constant-time byte comparison. Existing analyst/reviewer boundaries remain. Regression: status/source/history authorization test and existing API role tests.
- Draft editing previously accepted generation metadata/provider from the submitted narrative. The server now preserves original provider, generation metadata and unchanged-summary status; modified summaries are explicitly marked for revalidation. Revision actor/time/prior hash are server-created. Regression: forged generation/provider/status plus stale edit test.
- Configured external narrative URLs reject embedded credentials, query and fragment components, reducing accidental endpoint-secret exposure in exception records. Regression: credential-bearing URL rejected. Operator-configured endpoints still require proper trust; this is not a general secret-redaction layer.
- New source inspection is case-scoped and checks dataset identity; it exposes anonymous numerical attributes without benchmark labels. New status/model/history endpoints require the same authorization as existing routes; response whitelists exclude role tokens and encryption keys. Tests check unauthenticated access, out-of-case transaction denial and secret absence.
- pytest.ini limits discovery to tests/ so preserved copies and executable helper scripts are not collected. No existing test was deleted.

## Inspected controls retained

SQL query values use parameters. Case IDs do not become filesystem paths. Artifact/data paths are operator configuration rather than API-submitted paths. Torch checkpoint loading uses weights_only=True; baseline arrays use allow_pickle=False; local Transformers uses local_files_only. Download/unpack helpers restrict artifact members; runtime does not execute user-supplied shell commands. Model eval() calls are inference mode, not Python eval on external text.

Dynamic HTML uses escaping, script/style/connect sources are same-origin under CSP, and responses carry no-store/nosniff. The unnecessary empty CSS import was removed. API mutations reject differing Origin; tokenless mode limits host/client to loopback. Optional role tokens and encryption remain tested. No new bypass of final-state locks, revision checks, required notes or consistency findings is permitted. New generated text is checked as claims, not treated as instructions.

## Privacy boundaries

Elliptic transaction IDs remain anonymous transactions, never inferred people/accounts. Dataset time steps are not calendar dates. Synthetic reference snapshots explicitly declare synthetic_demo, include source/version/hash and require explicit synthetic entity linkage. Benchmark fixture configuration is rejected, and benchmark dossier reference results stay unavailable. Synthetic profiles/matches are supplemental demo context, excluded from benchmark claims and local LLM evidence.

Default extractive/local modes do not call an external narrative service. Ollama is explicit configuration; its URL is not included in status. No remote provider call was made in this review. Case content, reviewer notes and failures are persisted for traceability; unexpected service exceptions can still contain provider-returned text. Do not place secrets in evidence/notes. There is no comprehensive log-redaction or retention service.

## Remaining security limits

Loopback demo reviewer is a shared local role, not an authenticated individual. Production IAM, per-case tenancy/authorization, rate limiting, upload isolation, key rotation, secure backup retention and deployment hardening remain future work. Optional encryption protects payloads, not every artifact/metadata field. Local audit hash chains lack an external trusted anchor. Status filesystem timestamps are not signed attestations. Bearer mode must use appropriate TLS/network configuration for remote use. No assertion that all vulnerabilities or dependencies are risk-free is made.

## Dependency review

No new runtime dependency added or removed. NumPy/pandas load and transform graph data; torch/PyG implement the model/explainer; sklearn implements baseline, retrieval and diagnostics; SHAP explains the baseline; Transformers/sentencepiece/protobuf support local generation; FastAPI/uvicorn serve the API; httpx supports the optional provider and test client; cryptography supports payload encryption; pytest is the test dependency. These have active uses. Standard-library graph algorithms and frontend SVG avoid adding NetworkX/D3/matplotlib. A first diagnostic rendering attempt found matplotlib absent; removed the optional plotting dependency and retained real JSON tables and browser SVG curves. No result was fabricated to replace that failure.

requirements-lock.txt is preserved byte-for-byte; environment versions were not silently refreshed. Three upstream deprecation warnings remain in the passing test suite (torch scripting and Starlette/httpx/AnyIO interfaces). No package upgrade was made merely to silence them.
