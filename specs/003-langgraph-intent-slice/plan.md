# Implementation Plan: LangGraph Intent Slice

**Branch**: `[003-langgraph-intent-slice]` | **Date**: 2026-08-25 | **Spec**: [/specs/003-langgraph-intent-slice/spec.md](/specs/003-langgraph-intent-slice/spec.md)

**Input**: Feature specification from `/specs/003-langgraph-intent-slice/spec.md`

## Summary

Add the second backend vertical slice by introducing a LangGraph-driven chat path that classifies
intent and routes direct_response requests to real LLM generation while returning a fixed
unsupported placeholder for non-direct intents. Preserve all stage-1 validation, error-shape, and
disconnect behavior, extend stream events with `intent`, and keep scope limited to `src/agent/`,
`src/schemas/`, `src/api/routes/chat.py`, and contract tests.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, LLM client adapter (project-selected), pytest, httpx

**Storage**: N/A

**Testing**: pytest contract tests for `/chat/stream` and `/health`, including regression checks from stage-1

**Target Platform**: Linux/Windows server runtime for local dev and CI

**Project Type**: Backend web service

**Performance Goals**: Maintain existing stage-1 behavior latency envelope while adding classification and generation path; intent event emitted before token events in 100% of successful flows

**Constraints**:
- Add only `src/agent/` modules for state, graph, classification, generation, and prompt definitions
- Extend `src/schemas/chat.py` `ChatStreamEvent.event_type` with `intent`
- Extend `src/api/routes/chat.py` to route through LangGraph while preserving existing validation and disconnect semantics
- Extend tests for direct_response success, non-direct placeholder flow, and direct_response LLM-failure flow
- Do not create `src/rag/`, `src/tools/`, `src/security/`, or `src/observability/`
- Do not modify stage-1 validation/error-code/disconnect behavior beyond LangGraph routing integration

**Scale/Scope**: Single service instance MVP slice focused on routing + generation behavior with no tool/RAG subsystems

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Scope targets one complete end-to-end extension of chat path.
2. RAG-only policy grounding: PASS (N/A for this direct-response slice; no policy-answer path is introduced).
3. Secure FastMCP tooling: PASS (N/A this slice; no tool execution introduced).
4. PII redaction pre-LLM: PASS with explicit defer-by-scope for this pass.
5. Prompt-injection resistance: PASS with explicit defer-by-scope for this pass.
6. Stateful orchestration via LangGraph: PASS. This slice introduces LangGraph state graph.
7. Schema-first contracts: PASS. Chat stream schema is extended, existing boundaries preserved.
8. Fail-safe behavior: PASS. Non-direct intents route to deterministic placeholder; generation failure emits error event.
9. Honest Copilot documentation: PASS as process requirement for implementation change set.

Post-Phase 1 design re-check:
All gates remain PASS for this scoped feature.

## Project Structure

### Documentation (this feature)

```text
specs/003-langgraph-intent-slice/
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
│   ├── state.py
│   ├── graph.py
│   ├── nodes.py
│   └── prompts.py
├── api/
│   └── routes/
│       └── chat.py
└── schemas/
    └── chat.py

tests/
└── contract/
    ├── test_chat_stream.py
    └── test_health.py
```

**Structure Decision**: Keep existing backend service layout and add only the minimal agent modules plus
targeted schema/API/test extensions required for this vertical slice.

## Complexity Tracking

No constitution violations requiring exception records.
