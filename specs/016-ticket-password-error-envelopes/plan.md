# Implementation Plan: Ticket Password Error Envelopes (Feature 016)

**Branch**: `016-ticket-password-error-envelopes` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/016-ticket-password-error-envelopes/spec.md`

## Summary

Standardize the three remaining ticket-creation and password-reset error paths to serialize the project’s established `{error_code, message}` envelope into the existing `AgentState.error` field. Preserve the existing ticket category-guidance wording, add path-specific failure codes, and derive a non-empty fallback message for silent tool exceptions. No routing, inference, schema, event, or other-node change is needed.

## Technical Context

**Language/Version**: Python 3.14 (repository virtual environment)

**Primary Dependencies**: FastAPI, LangGraph, pytest, existing JSON standard-library support

**Storage**: N/A; error envelopes are ephemeral stream state

**Testing**: Existing pytest chat stream contract suite, followed by full pytest regression suite

**Target Platform**: FastAPI/LangGraph service on the current Windows development environment

**Project Type**: Stateful LangGraph web service with stream-event API

**Performance Goals**: Envelope construction adds no network or tool call and occurs within existing terminal error handling

**Constraints**: Touch only the missing-category and tool-exception branches in `create_ticket_node` and the tool-exception branch in `check_password_reset_node`; preserve intent/error order, no done behavior, inference logic, routing, schemas, and all success/escalation paths

**Scale/Scope**: Three error branches in `src/agent/nodes.py` and focused assertions in the existing chat stream contract test file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Vertical Slice First, End-to-End Always Works**: PASS. The repair preserves and verifies the existing ticket and password-reset vertical flows while making failure events consumable.

**Principle II - RAG-Only, Policy-Grounded Answers**: NOT APPLICABLE. No policy retrieval or answer generation changes are made.

**Principle III - Secure Tooling via Schema-Validated FastMCP**: PASS. Tool invocation and validation remain untouched; only terminal error formatting changes.

**Principle IV - Privacy by Default with Pre-LLM PII Redaction**: PASS. PII flow is unchanged and the plan does not expose raw traceback data.

**Principle V - Prompt Injection Resistance and Fail-Safe Outcomes**: PASS. This improves consistent, recoverable error outcomes and does not alter guardrails.

**Stateful Orchestration and Data Contracts**: PASS. The design reuses the existing `AgentState.error` serialized payload boundary and existing stream error event without changing LangGraph routing.

**GATE RESULT (pre-design)**: PASS. No complexity tracking is required.

## Project Structure

### Documentation (this feature)

```text
specs/016-ticket-password-error-envelopes/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
src/
├── agent/
│   └── nodes.py                   # MODIFY: three terminal error branches
├── api/
│   └── routes/chat.py             # Existing event behavior, unchanged
└── tools/                          # Existing calls, unchanged

tests/
└── contract/
    └── test_chat_stream.py        # MODIFY: existing error-path assertions
```

**Structure Decision**: Use the existing single web-service structure. Only `src/agent/nodes.py` requires runtime changes; existing contract tests validate the outer stream event and serialized inner envelope.

## Post-Design Constitution Check

**GATE RESULT (post-design)**: PASS. The design affects three existing terminal error values only, preserves all state transitions and tool behavior, and uses focused end-to-end stream contract tests.
