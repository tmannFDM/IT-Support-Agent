# Implementation Plan: Chat Stream Vertical Slice

**Branch**: `[001-chat-stream-slice]` | **Date**: 2026-08-25 | **Spec**: [/specs/001-chat-stream-slice/spec.md](/specs/001-chat-stream-slice/spec.md)

**Input**: Feature specification from `/specs/001-chat-stream-slice/spec.md`

## Summary

Deliver the first backend vertical slice for chat transport plumbing only: a validated
`POST /chat/stream` endpoint that streams SSE events (`token`, `done`) without any LLM,
RAG, agent, or tool execution, plus a `GET /health` endpoint and basic contract tests.
The design enforces schema-first boundaries using Pydantic v2 and intentionally limits
implementation scope to `src/api/`, `src/schemas/`, and `tests/`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, pytest, httpx

**Storage**: N/A (no persistence in this slice)

**Testing**: pytest + FastAPI TestClient/httpx for API contract checks

**Target Platform**: Linux/Windows server runtime for local dev and CI

**Project Type**: Backend web service (single FastAPI app)

**Performance Goals**: First SSE token emitted within 500 ms for local acceptance tests;
`/health` responds in under 100 ms in local test conditions

**Constraints**:
- Only create and modify `src/api/`, `src/schemas/`, and `tests/`
- Do not create `src/agent/`, `src/rag/`, `src/tools/`, `src/security/`, or `src/observability/`
- Use schema-based request/response validation at all layer boundaries
- Return machine-readable validation error code `ERR-VALIDATION-MISSING-FIELD`

**Scale/Scope**: Single service instance, low-volume MVP validation traffic (<50 concurrent
test clients), no distributed components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. This feature delivers a complete and demonstrable API-to-stream
  path and avoids breadth expansion.
2. RAG-only policy grounding: PASS (N/A for this slice). No model inference path exists yet,
  so no policy-answer generation occurs.
3. FastMCP schema-validated tools: PASS (N/A for this slice). No tool execution is included.
4. PII redaction before LLM: PASS (N/A for this slice). No LLM calls are permitted.
5. Prompt injection resistance and fail-safe outcomes: PASS (N/A for this slice). No prompt
  execution path is present.
6. Stateful orchestration via LangGraph: PASS (Deferred by explicit scope boundary in spec for
  this pass).
7. Schema-first contracts: PASS. Request and stream event contracts are Pydantic v2-first.
8. Fail-safe behavior under uncertainty: PASS. Slice does not claim decision intelligence.
9. Honest Copilot usage documentation: PASS with process requirement for implementation PRs.

Post-Phase 1 design re-check:
All gates remain PASS under the same scope interpretation and constraints.

## Project Structure

### Documentation (this feature)

```text
specs/001-chat-stream-slice/
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
├── api/
│   ├── routes/
│   │   ├── chat.py
│   │   └── health.py
│   └── sse.py
└── schemas/
   ├── chat.py
   └── support.py

tests/
└── contract/
   ├── test_chat_stream.py
   └── test_health.py
```

**Structure Decision**: Use a single-service layout centered on API boundary contracts. The
structure intentionally excludes agent, RAG, tools, security, and observability modules in this
pass, per feature scope.

## Complexity Tracking

No constitution violations requiring exception are identified for this scoped transport slice.
