# Implementation Plan: FastMCP Ticket Status Slice

**Branch**: `[004-fastmcp-ticket-status]` | **Date**: 2026-08-25 | **Spec**: [/specs/004-fastmcp-ticket-status/spec.md](/specs/004-fastmcp-ticket-status/spec.md)

**Input**: Feature specification from `/specs/004-fastmcp-ticket-status/spec.md`

## Summary

Deliver the next backend vertical slice by replacing ticket-status placeholder behavior with a
real FastMCP tool flow backed by a mocked in-memory ticket store. Route only ticket-status
action requests to a new `check_ticket_status` node, validate tool input/output through Pydantic
schemas, and preserve all existing stage-1/stage-2 validation, error-code, disconnect, and non-
ticket behavior contracts. Keep stream envelope unchanged (`ChatStreamEvent.data: str`) while
serializing validated tool output JSON into `tool_call` events.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, FastMCP, pytest, httpx

**Storage**: In-memory mocked ticket dictionary only (no persistent database)

**Testing**: pytest contract tests under `tests/contract`

**Target Platform**: Backend service runtime on Windows/Linux for local dev and CI

**Project Type**: Backend web service

**Performance Goals**:
- Maintain existing chat stream responsiveness for this slice
- Keep successful ticket-status flows completing with full event sequence in under 2s for local verification target

**Constraints**:
- Add only scoped modules and updates requested for this pass:
  - `src/tools/` for FastMCP `ticket_status_lookup` and in-memory sample ticket store
  - `src/schemas/` additions for `TicketStatusRequest` and `TicketStatusResponse`
  - `src/agent/` additions for ticket-ID extraction, `check_ticket_status` node, and routing updates
  - `src/api/routes/chat.py` extension only for `tool_call` event handling with JSON-serialized `data: str`
  - `tests/` contract coverage for valid ID, missing ID, and unknown ID flows
- Do not add `src/rag/` or `src/security/`
- Do not add password-reset or ticket-creation tools
- Do not modify stage-1/stage-2 validation semantics, error-code contracts, disconnect handling, or unrelated classification behavior
- Ticket ID extraction format is fixed to `TKT-<digits>` (case-insensitive input; normalized to `TKT-<digits>` before lookup)
- `TicketStatusResponse.last_updated` must use UTC ISO 8601 with `Z` suffix

**Scale/Scope**: Single vertical slice for ticket-status lookup only, with small deterministic mock ticket set

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. This adds one complete end-to-end capability for ticket status.
2. RAG-only policy grounding: PASS (N/A for this operational status lookup path; no policy-answer feature added).
3. Secure FastMCP tooling via schema validation: PASS. Feature explicitly adds FastMCP tool with Pydantic input/output validation.
4. Privacy by default (PII redaction): PASS with explicit defer-by-scope; no new redaction mechanism added this pass.
5. Prompt injection resistance/fail-safe: PASS with scoped fail-safe behavior (missing ticket ID returns user-correctable error, unknown ID returns expected not-found token).
6. Stateful orchestration via LangGraph: PASS. Routing remains in graph with explicit ticket-status node.
7. Schema-first contracts: PASS. New request/response schemas and stream contract behavior are explicit.
8. End-to-end verification gate: PASS by planned contract tests and regression checks.
9. Honest Copilot usage documentation: PASS as process requirement during implementation PR/change record.

Post-Phase 1 design re-check:
All gates remain PASS for this scoped design.

## Project Structure

### Documentation (this feature)

```text
specs/004-fastmcp-ticket-status/
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
│   ├── prompts.py
│   └── state.py
├── api/
│   └── routes/
│       └── chat.py
├── schemas/
│   ├── chat.py
│   └── ticket_status.py          # new
└── tools/
    ├── __init__.py               # new
    ├── ticket_store.py           # new
    └── ticket_status_tool.py     # new FastMCP tool

tests/
└── contract/
    ├── test_chat_stream.py
    └── test_health.py
```

**Structure Decision**: Preserve the existing backend-only service layout and add only minimal
modules required for the ticket-status tool slice, with no RAG/security/frontend expansion.

## Complexity Tracking

No constitution violations requiring exception records.
