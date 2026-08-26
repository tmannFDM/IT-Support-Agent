# Implementation Plan: PII Redaction and Prompt Injection Guard

**Branch**: `[006-pii-injection-guard]` | **Date**: 2026-08-26 | **Spec**: [/specs/006-pii-injection-guard/spec.md](/specs/006-pii-injection-guard/spec.md)

**Input**: Feature specification from `/specs/006-pii-injection-guard/spec.md`

## Summary

Add a pre-classification guardrail step that runs deterministic prompt-injection detection and
PII redaction before any intent classification, RAG retrieval, tool calls, or LLM prompts.
Injection attempts are short-circuited to an immediate `error` event with JSON-encoded
`ERR-PROMPT-INJECTION-BLOCKED` details and fixed message `Request blocked for safety.`.
Non-blocked messages continue through existing flow; if PII is present it is masked in-place
using visible placeholders for downstream use.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, httpx, pytest

**Storage**: N/A (no persistent storage changes)

**Testing**: pytest contract tests (`tests/contract/test_chat_stream.py`, `tests/contract/test_health.py`)

**Target Platform**: Backend service on Windows/Linux local and CI runtimes

**Project Type**: Backend web service

**Performance Goals**:
- Guardrail checks add minimal latency and preserve existing stream responsiveness.
- Existing successful stream ordering remains unchanged for clean/non-blocked requests.

**Constraints**:
- Add only `src/security/` for `redact_pii` and `detect_prompt_injection`.
- Add only minimal `src/agent/` guardrail integration before `classify_intent`.
- Blocked messages must emit `error` as first event, with JSON-encoded string in `data`.
- Exact blocked message text: `Request blocked for safety.`.
- Pattern detection is deterministic keyword/pattern matching only (no second LLM call).
- Keep existing stage 1-4 validation/error-code/disconnect handling semantics unchanged,
  except earlier guardrail short-circuit for blocked injection requests.
- No `src/tools/` additions, no `src/observability/`, no password-reset/ticket-creation work.

**Scale/Scope**: One vertical slice covering ingress safety checks and regression-preserving stream behavior.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Delivers one complete safety slice integrated end to end.
2. RAG-only policy grounding: PASS. RAG behavior is preserved; guardrail runs earlier at ingress.
3. Secure tooling via schema-validated FastMCP: PASS. No tooling contract changes in this slice.
4. Privacy by default with pre-LLM PII redaction: PASS. This slice directly implements this principle.
5. Prompt injection resistance and fail-safe outcomes: PASS. Deterministic blocking before downstream processing.
6. Stateful orchestration and contracts: PASS. Integrates guardrail into existing graph/stream contract.
7. End-to-end verification gate: PASS with required contract/regression tests.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All gates remain PASS for this scoped feature.

## Project Structure

### Documentation (this feature)

```text
specs/006-pii-injection-guard/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
  └── http-api.md
```

### Source Code (repository root)

```text
src/
├── security/
│   ├── redact.py                 # new: email/phone masking helpers
│   └── injection.py              # new: normalized prompt-injection matching
├── agent/
│   ├── state.py                  # possible extension for guardrail/block metadata
│   ├── nodes.py                  # guardrail node before classification
│   └── graph.py                  # route guardrail check before classify_intent
└── api/
    └── routes/
        └── chat.py               # blocked-first stream error behavior

tests/
└── contract/
    └── test_chat_stream.py       # new guardrail and regression assertions
```

**Structure Decision**: Keep existing backend layout; add `src/security/` for deterministic safety
checks and insert a pre-classification guardrail step in agent flow with minimal route changes.

## Complexity Tracking

No constitution violations requiring exceptions.
