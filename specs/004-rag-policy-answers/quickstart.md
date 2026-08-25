# Quickstart: Validate RAG Policy Answers Slice

## Prerequisites
- Python 3.11+
- Existing backend service baseline from prior slices
- Local Ollama runtime with `llama3.2:3b` available
- Local embedding model execution capability for `all-MiniLM-L6-v2`

## Scope for this pass
Add only:
- `src/rag/` ingestion + embedding + retrieval logic
- `src/agent/` policy answer node and policy routing updates
- route wiring changes needed for policy path output
- contract tests for on-topic, off-topic fallback, and cross-category questions

Do not add:
- `src/tools/` additions
- `src/security/`
- `src/observability/`
- password reset or ticket creation tool changes
- unrelated validation/disconnect/error behavior changes

## Prepare policy corpus
- Ensure these files exist and are used as-is:
  - `src/rag/policy_docs/vpn_policy.md`
  - `src/rag/policy_docs/password_policy.md`
  - `src/rag/policy_docs/hardware_policy.md`
  - `src/rag/policy_docs/software_policy.md`
  - `src/rag/policy_docs/access_policy.md`

## Run service

```bash
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
```

## Validation Scenario A: on-topic grounded policy answer
Ask a question clearly answerable from one policy document (for example VPN policy question).

Expected:
1. stream starts with `intent` (`policy_question`)
2. response emitted as `token` event(s)
3. answer content is grounded in retrieved policy text
4. answer includes source filename citation(s), for example `Source: vpn_policy.md`
5. stream ends with `done`

## Validation Scenario B: off-topic fallback
Ask a policy-style question not covered by available policy docs.

Expected:
1. stream starts with `intent`
2. token content is exactly: `I don't have information on that policy.`
3. stream ends with `done`
4. no hallucinated policy details

## Validation Scenario C: cross-category policy question
Ask a question spanning at least two policy categories (for example VPN + password).

Expected:
1. retrieval context includes chunks from more than one `source_document`
2. answer remains grounded in retrieved context
3. answer includes relevant source filename citations
4. stream ends with `done`

## Validation Scenario D: policy generation failure behavior
Simulate/force LLM failure in policy path.

Expected:
1. `intent` event first
2. `error` event second
3. stream terminates without `done`

## Validation Scenario E: regression checks
Run existing non-policy scenarios and prior contract tests.

Expected unchanged:
- stage-1 validation behavior
- stage-1 disconnect behavior
- stage-2 direct_response path
- stage-3 ticket_status action_request path

## Run tests

```bash
.\.venv\Scripts\python.exe -m pytest -q tests
```

Expected:
- existing tests remain passing
- new policy contract tests pass for:
  - grounded on-topic answer
  - fixed off-topic fallback
  - cross-category retrieval grounding

## Verification Notes

- Latest run: `15 passed, 2 warnings` via `./.venv/Scripts/python.exe -m pytest -q tests`.
- Validation error and disconnect behavior remain covered by contract tests.
