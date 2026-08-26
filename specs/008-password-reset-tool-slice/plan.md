# Implementation Plan: Password Reset Tool Slice

**Branch**: `[008-password-reset-tool-slice]` | **Date**: 2026-08-26 | **Spec**: [/specs/008-password-reset-tool-slice/spec.md](/specs/008-password-reset-tool-slice/spec.md)

**Input**: Feature specification from `/specs/008-password-reset-tool-slice/spec.md`

## Summary

Add a sixth vertical slice that replaces the password-reset action-request placeholder
with a FastMCP-backed password reset flow. The flow adds schema-validated request/response
contracts, deterministic suspicion checks (invalid employee ID, urgency pressure,
vague reason), single-reason precedence, and stream-safe outcomes:
intent then tool_call or token then done, with existing intent then error behavior
preserved for unexpected tool failure.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, FastMCP tooling layer, pytest

**Storage**: In-memory mock tool state only for this slice

**Testing**: pytest contract/regression tests in tests/contract/test_chat_stream.py and tests

**Target Platform**: Backend service on local and CI environments

**Project Type**: Backend web service

**Performance Goals**:
- Preserve existing stream latency profile for non-password flows.
- Keep password-reset suspicion checks deterministic and lightweight string/rule evaluation.

**Constraints**:
- Implement only scoped additions:
  - src/tools: password_reset FastMCP tool with mocked in-memory behavior and fixed temporary password note.
  - src/schemas: PasswordResetRequest and PasswordResetResponse.
  - src/agent: password-reset node/routing logic with normalization-consistent urgency matching.
  - tests: targeted contract coverage for success/escalation precedence and no-regression behavior.
- Do not modify ticket_status_lookup behavior, RAG retrieval path, or stage-5 guardrail semantics.
- Do not add ticket creation tooling or long-term memory components.
- Never expose or generate an actual password value.

**Scale/Scope**: One new vertical workflow plus route split inside existing action_request handling.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. This is a complete end-to-end password-reset slice replacing a placeholder.
2. RAG-only policy grounding: PASS. Policy/RAG pipeline remains unchanged; this adds tool-assisted action flow.
3. Secure tooling via schema-validated FastMCP: PASS. Tool contract is schema-first with explicit request/response models.
4. Privacy by default: PASS. No new raw credential collection; current redaction behavior remains intact.
5. Prompt injection resistance and fail-safe outcomes: PASS. Suspicious signals trigger escalation instead of automated reset.
6. Stateful orchestration and data contracts: PASS. LangGraph node/routing and Pydantic contracts remain explicit.
7. End-to-end verification gate: PASS contingent on targeted contract tests and full-suite regression.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All gates remain PASS for the constrained implementation scope.

## Project Structure

### Documentation (this feature)

```text
specs/008-password-reset-tool-slice/
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
├── agent/
│   ├── nodes.py
│   └── graph.py
├── schemas/
│   └── password_reset.py      # new schema models for tool IO
└── tools/
    └── password_reset.py      # new FastMCP tool + mocked in-memory logic

tests/
└── contract/
    └── test_chat_stream.py    # password-reset success/escalation and no-regression checks
```

**Structure Decision**: Extend current backend layout with one new tool module, one new schema module,
and focused agent routing/node updates while preserving existing ticket-status, policy, and guardrail flows.

## Complexity Tracking

No constitution violations requiring exception records.
