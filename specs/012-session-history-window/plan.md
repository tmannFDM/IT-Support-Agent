# Implementation Plan: In-Session Conversation History Window

**Branch**: `[012-session-history-window]` | **Date**: 2026-08-31 | **Spec**: [/specs/012-session-history-window/spec.md](/specs/012-session-history-window/spec.md)

**Input**: Feature specification from `/specs/012-session-history-window/spec.md`

## Summary

Add the ninth vertical slice for short-term, session-scoped conversation memory with a fixed sliding window of 5 completed exchanges. Keep storage ephemeral and keyed by `session_id`, append redacted user/assistant turn pairs only after response completion, inject recent history into direct and policy LLM calls, and leave ticket status/password reset/ticket creation extraction-routing flows unchanged. Validate with contract tests for same-session continuity, cross-session isolation, bounded eviction, and tool-path non-regression.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, LangGraph, Pydantic v2, httpx, pytest

**Storage**: In-memory process-local session history store (ephemeral dict/deque style), separate from long-term JSON-backed user memory

**Testing**: pytest contract tests in `tests/contract/test_chat_stream.py`, plus full `tests` regression run

**Target Platform**: Backend API service runtime (local dev + CI)

**Project Type**: Backend web service

**Performance Goals**:
- Bound prompt-growth cost for context-aware follow-ups by capping history to 5 exchanges/session.
- Preserve current response streaming behavior and ordering while adding post-completion history capture.

**Constraints**:
- For implementation scope, change only `src/agent/` (including a small session-history module if needed) and `tests/` for this pass.
- Session history entries must store redacted text only.
- Append history only after request completion event (`done`) and never before completion.
- Inject history only for direct-response and policy-question LLM calls.
- Keep ticket-status, password-reset, and ticket-creation extraction/routing logic unchanged and history-independent.
- Do not modify long-term user memory semantics, tool implementations, RAG retrieval behavior, or guardrail detection/redaction semantics beyond reading already-redacted `state["message"]`.

**Scale/Scope**: One feature slice for in-session context continuity across short multi-turn conversations with strict session isolation and bounded memory.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Defines end-to-end behavior from chat request through LLM prompt enrichment and completion-time capture.
2. RAG-only policy grounding: PASS. Policy responses remain grounded in retrieved chunks; history is additive conversational context, not a replacement for retrieval.
3. Secure tooling/schema contracts: PASS. Tooling paths remain unchanged; no new privileged tool surface introduced.
4. Privacy by default with pre-LLM redaction: PASS. Stored session history is explicitly redacted-only and sourced from already-redacted input plus final response text.
5. Prompt injection resistance and fail-safe outcomes: PASS. Guardrail and fail-safe flow remain unchanged.
6. Stateful orchestration and data contracts: PASS. Session history behavior is stateful and constrained to explicit session key boundaries.
7. End-to-end verification: PASS with required contract tests for continuity, isolation, eviction, and non-regression.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All constitution gates remain PASS for the scoped in-session history design.

## Project Structure

### Documentation (this feature)

```text
specs/012-session-history-window/
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
│   ├── state.py
│   └── session_history.py        # planned new module
├── api/
│   └── routes/
│       └── chat.py
├── memory/
│   └── store.py                  # unchanged long-term memory module
└── tools/
    ├── password_reset.py         # unchanged
    ├── create_ticket.py          # unchanged
    └── ticket_store.py           # unchanged

tests/
└── contract/
    └── test_chat_stream.py
```

**Structure Decision**: Keep the existing single-project backend structure and implement session-history behavior with minimal targeted changes in `src/agent/` plus contract tests in `tests/contract/test_chat_stream.py`, without broad refactors.

## Complexity Tracking

No constitution violations requiring exception records.
