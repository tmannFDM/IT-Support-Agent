# Implementation Plan: Ticket Creation Tool Slice

**Branch**: `[010-ticket-creation-tool-slice]` | **Date**: 2026-08-26 | **Spec**: [/specs/010-ticket-creation-tool-slice/spec.md](/specs/010-ticket-creation-tool-slice/spec.md)

**Input**: Feature specification from `/specs/010-ticket-creation-tool-slice/spec.md`

## Summary

Deliver the seventh vertical slice by replacing action-request ticket-creation placeholder behavior with a schema-validated FastMCP `create_ticket` tool path. The pass is intentionally narrow: add ticket creation schemas and tooling, add ticket-creation node/routing with deterministic keyword inference and mixed-intent precedence, and extend contract tests. Keep existing ticket-status lookup logic, password-reset tooling, RAG flow, and guardrail logic unchanged except for minimal routing integration.

## Technical Context

**Language/Version**: Python 3.11+ (project runtime currently validated on Python 3.14.5 venv)

**Primary Dependencies**: FastAPI, LangGraph, Pydantic v2, pytest

**Storage**: In-memory mocked ticket store shared by ticket creation and ticket-status lookup flows

**Testing**: pytest contract tests (`tests/contract/test_chat_stream.py`) plus full regression suite (`tests`)

**Target Platform**: Backend service (Windows local dev and CI-compatible Python runtime)

**Project Type**: Backend web service

**Performance Goals**:
- Preserve deterministic SSE event ordering for action requests.
- Keep ticket creation inference/id-generation overhead negligible relative to current action-request path.

**Constraints**:
- Only add behavior in these areas for this pass: `src/tools/`, `src/schemas/`, `src/agent/`, and `tests/contract/`.
- Do not modify existing ticket-status lookup logic internals; only write through its shared in-memory store.
- Do not modify password-reset tool behavior, RAG pipeline behavior, or guardrail policy behavior.
- Mixed-intent precedence is fixed: valid ticket ID in message routes to status-lookup path before create intent.
- Category precedence is fixed: Access > VPN > Password > Hardware > Software.
- Default priority when no severity keywords are found is `medium`.

**Scale/Scope**: Single vertical slice addition for ticket creation requests with regression-safe integration into existing stream contract.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Adds a complete actionable path (intent -> tool_call -> token -> done) for ticket creation.
2. RAG-only policy grounding: PASS. Policy-question retrieval/grounding path remains untouched.
3. Secure tooling via schema-validated FastMCP: PASS. New tool is explicitly schema-backed via Pydantic request/response.
4. Privacy by default: PASS. No change to pre-LLM redaction flow; creation logic uses already-redacted message pipeline.
5. Prompt injection resistance and fail-safe outcomes: PASS. Existing guardrail remains in front; uncategorizable create requests fail safe with explicit error.
6. Stateful orchestration and data contracts: PASS. LangGraph routing is extended with explicit branch logic and structured `tool_call` payload.
7. End-to-end verification gate: PASS with added contract tests and full-suite regression run.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All constitution gates remain PASS for the constrained ticket-creation slice.

## Project Structure

### Documentation (this feature)

```text
specs/010-ticket-creation-tool-slice/
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
│   ├── nodes.py
│   └── state.py
├── schemas/
│   ├── __init__.py
│   └── ticket_create.py           # new
└── tools/
    ├── __init__.py
    ├── create_ticket.py           # new
    └── ticket_store.py            # shared store module (existing or added as integration seam)

tests/
└── contract/
    └── test_chat_stream.py
```

**Structure Decision**: Keep a single backend project layout and introduce minimal new modules under existing `src/schemas` and `src/tools`, then extend `src/agent` routing/nodes and contract tests for deterministic creation/status precedence behavior.

## Complexity Tracking

No constitution violations requiring exceptions.
