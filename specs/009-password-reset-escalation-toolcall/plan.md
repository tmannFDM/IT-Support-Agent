# Implementation Plan: Password Reset Escalation ToolCall Fix

**Branch**: `[009-password-reset-escalation-toolcall]` | **Date**: 2026-08-26 | **Spec**: [/specs/009-password-reset-escalation-toolcall/spec.md](/specs/009-password-reset-escalation-toolcall/spec.md)

**Input**: Feature specification from `/specs/009-password-reset-escalation-toolcall/spec.md`

## Summary

Fix password-reset escalation stream output so escalation metadata is emitted as
structured PasswordResetResponse tool_call data (status=escalated) instead of leaking
internal field fragments in token text. Preserve existing event sequence and prior-stage
behavior by changing only check_password_reset escalation content composition and
stream emission behavior only if required for tool_call on escalation.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, pytest

**Storage**: N/A

**Testing**: pytest contract tests in tests/contract/test_chat_stream.py plus full tests suite

**Target Platform**: Backend service on local and CI environments

**Project Type**: Backend web service

**Performance Goals**:
- Keep stream behavior deterministic with no additional event types or extra branching overhead.
- Maintain prior response latency profile for all existing flows.

**Constraints**:
- This pass only touches src/agent/nodes.py and src/api/routes/chat.py if needed.
- No new files and no schema changes.
- No changes to reset success path semantics.
- No changes to ticket-status, RAG, or stage-5 guardrail behavior.

**Scale/Scope**: Targeted bug fix for escalation content events only.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Fixes a production-path bug in an existing complete slice.
2. RAG-only policy grounding: PASS. No RAG behavior touched.
3. Secure tooling via schema-validated FastMCP: PASS. Escalation now uses existing structured schema payload channel.
4. Privacy by default: PASS. Removes internal field-name leakage from user-visible tokens.
5. Prompt injection resistance and fail-safe outcomes: PASS. Escalation decision logic remains fail-safe and unchanged.
6. Stateful orchestration and data contracts: PASS. Preserves graph/event contracts and strengthens structured output consistency.
7. End-to-end verification gate: PASS with updated escalation-order contract tests and full-suite regression.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All gates remain PASS for this constrained bug-fix scope.

## Project Structure

### Documentation (this feature)

```text
specs/009-password-reset-escalation-toolcall/
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
│   └── nodes.py
└── api/
    └── routes/
        └── chat.py

tests/
└── contract/
    └── test_chat_stream.py
```

**Structure Decision**: Restrict runtime edits to escalation payload/token composition in
src/agent/nodes.py and stream emission in src/api/routes/chat.py only if required,
plus contract test assertion updates for escalation ordering.

## Complexity Tracking

No constitution violations requiring exception records.
