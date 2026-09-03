# Implementation Plan: Error Envelope Fallback (Feature 015)

**Branch**: `015-error-envelope-fallback` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/015-error-envelope-fallback/spec.md`

## Summary

Repair the generation-failure error contract without altering stream order or successful behavior. The two affected LangGraph nodes will serialize the established `error_code`/`message` envelope into the existing `AgentState.error` field and guarantee non-empty exception text. The existing frontend stream client will make `parseErrorPayload` tolerate empty, malformed, primitive, and structurally invalid data by returning its user-safe fallback instead of throwing. Scope is limited to `src/agent/nodes.py`, `frontend/src/api/chatStream.ts`, and focused contract tests required to verify the repaired behavior.

## Technical Context

**Language/Version**: Python 3.14 (repository virtual environment), TypeScript 5.4.5

**Primary Dependencies**: FastAPI, LangGraph, httpx, pytest; React 18.3.1 and Vite 5.4.21 frontend tooling

**Storage**: N/A; the error envelope is ephemeral stream state

**Testing**: pytest contract tests; frontend TypeScript production build; focused frontend parser tests when the repository test harness supports them

**Target Platform**: FastAPI service and modern browsers on Windows development environment

**Project Type**: Stateful LangGraph web service with React single-page frontend

**Performance Goals**: Error payload handling adds no network round trip and completes within the existing stream event processing path

**Constraints**: Preserve `intent → error` and no `done` for both generation failures; no new event type, schema, dependency, file, or changes to unrelated nodes/event handling

**Scale/Scope**: Two backend exception handlers and one frontend parser; existing direct-response and policy-question failure contract coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Vertical Slice First, End-to-End Always Works**: PASS. The repair protects the existing chat vertical slice from a known failure mode and will be verified through its existing stream contract tests.

**Principle II - RAG-Only, Policy-Grounded Answers**: PASS. Policy retrieval and response generation behavior are unchanged; only failure formatting is made consistent.

**Principle III - Secure Tooling via Schema-Validated FastMCP**: NOT APPLICABLE. No tools or tool schemas are changed.

**Principle IV - Privacy by Default with Pre-LLM PII Redaction**: PASS. PII handling is unchanged and raw exception data remains within the existing safe error rendering path.

**Principle V - Prompt Injection Resistance and Fail-Safe Outcomes**: PASS. The repair makes error outcomes fail-safe and does not alter prompt-injection handling.

**Stateful Orchestration and Data Contracts**: PASS. The feature uses the current `AgentState.error` boundary and formalizes its existing error envelope convention without adding raw parsing at a new cross-layer boundary.

**GATE RESULT (pre-design)**: PASS. No violations or exceptions require complexity tracking.

## Project Structure

### Documentation (this feature)

```text
specs/015-error-envelope-fallback/
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
│   ├── graph.py                   # Existing stream lifecycle remains unchanged
│   └── nodes.py                   # MODIFY: two generation exception handlers
├── api/
└── schemas/

tests/
└── contract/
  └── test_chat_stream.py        # MODIFY: focused generation-failure assertions

frontend/
├── src/
│   └── api/
│       └── chatStream.ts          # MODIFY: defensive error parsing
└── package.json
```

**Structure Decision**: Existing web-service plus frontend structure. No new runtime files or schemas are required; tests are limited to the existing contract suite and current frontend build surface.

## Post-Design Constitution Check

**GATE RESULT (post-design)**: PASS. The design reuses the existing serialized error state and stream error event, adds no cross-layer schema or lifecycle changes, preserves policy and guardrail behavior, and specifies focused regression verification.
