# Implementation Plan: RAG Policy Answers Slice

**Branch**: `[004-rag-policy-answers]` | **Date**: 2026-08-25 | **Spec**: [/specs/004-rag-policy-answers/spec.md](/specs/004-rag-policy-answers/spec.md)

**Input**: Feature specification from `/specs/004-rag-policy-answers/spec.md`

## Summary

Deliver the next vertical backend slice by replacing `policy_question` placeholder responses with
retrieval-grounded answers from existing markdown policy documents. The slice ingests policy docs
into ChromaDB with metadata, retrieves top-3 chunks using local sentence-transformers embeddings,
applies a 0.35 relevance threshold fail-safe fallback, and routes `policy_question` intent through
a new `answer_policy_question` node that calls local Ollama (`llama3.2:3b`) only when context is
sufficient. Existing stage-1/stage-2/stage-3 behavior remains unchanged outside policy routing.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, ChromaDB, sentence-transformers (`all-MiniLM-L6-v2`), Ollama local model runtime (`llama3.2:3b`), pytest

**Storage**: Local ChromaDB collection for policy chunks; source markdown docs under `src/rag/policy_docs/`

**Testing**: pytest contract tests under `tests/contract`

**Target Platform**: Backend service on local/CI Linux and Windows environments

**Project Type**: Backend web service

**Performance Goals**:
- Maintain current stream responsiveness for non-policy flows.
- Return policy responses using top-3 retrieval with minimal added latency appropriate for local embedding + local generation.

**Constraints**:
- Add only this pass scope:
  - `src/rag/` ingestion, embedding setup, and retrieval with 0.35 relevance threshold
  - `src/agent/` additions for `answer_policy_question` node and policy grounded generation flow
  - routing update so `policy_question` uses the new node
  - tests for on-topic grounding, off-topic fixed fallback, and cross-category retrieval
- Do not add `src/tools/` additions, `src/security/`, or `src/observability/`
- Do not modify ticket-status tool implementation/routing
- Do not change stage-1/stage-2 validation, error-code, disconnect semantics, or non-policy behaviors beyond required policy routing
- Fallback message must be exact: `I don't have information on that policy.`
- Successful policy answers append `source_document` filename provenance in final token content

**Scale/Scope**: Five existing policy markdown files only; single collection and single policy-answer path

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Adds one complete end-to-end capability for policy QA.
2. RAG-only policy grounding: PASS. Policy answers are retrieval constrained and fail safe when context is insufficient.
3. Secure tooling via schema-validated FastMCP: PASS (N/A for this slice; no new FastMCP tool introduced).
4. Privacy by default: PASS with scope defer; no new raw-data logging behavior introduced.
5. Prompt-injection resistance and fail-safe outcomes: PASS via explicit no-context fallback and grounded prompt constraints.
6. Stateful orchestration via LangGraph: PASS; policy path is implemented as explicit graph node.
7. Schema-first contracts: PASS; stream contract preserved and deterministic fallback behavior specified.
8. End-to-end verification gate: PASS by scoped contract tests and regression checks.
9. Honest Copilot documentation: PASS as implementation process requirement.

Post-Phase 1 design re-check:
All gates remain PASS for this scoped feature.

## Project Structure

### Documentation (this feature)

```text
specs/004-rag-policy-answers/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── http-api.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── agent/
│   ├── graph.py
│   └── nodes.py
├── api/
│   └── routes/
│       └── chat.py
├── rag/
│   ├── policy_docs/
│   │   ├── vpn_policy.md
│   │   ├── password_policy.md
│   │   ├── hardware_policy.md
│   │   ├── software_policy.md
│   │   └── access_policy.md
│   ├── ingest.py            # new
│   ├── retrieve.py          # new
│   └── embeddings.py        # new

tests/
└── contract/
    └── test_chat_stream.py
```

**Structure Decision**: Keep the current backend layout and add only `src/rag/` components plus
targeted agent/route/test changes needed for policy-question grounding.

## Complexity Tracking

No constitution violations requiring exception records.
