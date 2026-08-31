# Implementation Plan: Long-Term User Memory Whitelist

**Branch**: `[011-user-memory-whitelist]` | **Date**: 2026-08-26 | **Spec**: [/specs/011-user-memory-whitelist/spec.md](/specs/011-user-memory-whitelist/spec.md)

**Input**: Feature specification from `/specs/011-user-memory-whitelist/spec.md`

## Summary

Add an eighth vertical slice for durable, cross-session user memory with a strict three-field whitelist keyed by user_id. This pass is tightly scoped to JSON-file persistence in `src/memory/`, schema additions for whitelist facts, deterministic pattern-based extraction after PII redaction in guardrail flow, optional fact availability in response nodes, and contract tests proving cross-session retrieval, partial-valid updates, restart persistence, and no-regression behavior.

## Technical Context

**Language/Version**: Python 3.11+ (project currently runs on Python 3.14.5 venv)

**Primary Dependencies**: FastAPI, LangGraph, Pydantic v2, pytest

**Storage**: JSON-file-backed local persistence (for example `src/memory/user_memory.json`) keyed by user_id; no full database

**Testing**: pytest contract tests in `tests/contract/test_chat_stream.py` plus full regression suite in `tests`

**Target Platform**: Backend service runtime for local and CI execution

**Project Type**: Backend web service

**Performance Goals**:
- Maintain existing chat stream sequencing and response behavior when no facts are present.
- Keep per-request memory read/write overhead small enough to avoid noticeable response regression for current test flows.

**Constraints**:
- Add only: `src/memory/`, `src/schemas/` additions, `src/agent/` memory extraction and context wiring, and contract tests.
- Extraction must use deterministic keyword/pattern matching only; no LLM extraction.
- Persist only whitelist fields: preferred_device_type, office_region (APAC/EMEA/AMER), timezone abbreviation from fixed whitelist.
- Perform per-field partial updates: save valid facts and ignore invalid/non-whitelisted candidates in same message.
- Run extraction after redaction within/alongside guardrail flow before intent classification.
- Do not modify ticket, password-reset, RAG, or guardrail logic beyond minimal wiring needed for memory read/write.
- Explicitly out of scope: Arize Phoenix, Promptfoo, React frontend.

**Scale/Scope**: One vertical slice adding durable user memory facts with strict privacy boundaries and cross-session reuse by user_id.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. Adds a complete end-to-end memory fact capture and reuse slice in current chat flow.
2. RAG-only policy grounding: PASS. Policy-grounding behavior is unchanged; memory facts are optional context only.
3. Secure tooling/schema contracts: PASS. New facts are constrained by explicit schema literals and closed whitelist.
4. Privacy by default with pre-LLM redaction: PASS. Extraction runs after redaction and stores no PII/non-whitelisted fields.
5. Prompt-injection resistance and fail-safe outcomes: PASS. Existing guardrail order remains; absence of facts never blocks responses.
6. Stateful orchestration and data contracts: PASS. Agent state is extended with explicit optional memory facts.
7. End-to-end verification: PASS with required contract tests and full regression run.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All constitution gates remain PASS for this constrained memory-whitelist scope.

## Project Structure

### Documentation (this feature)

```text
specs/011-user-memory-whitelist/
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
├── memory/
│   ├── store.py                 # new
│   └── user_memory.json         # new runtime data file
├── schemas/
│   ├── __init__.py
│   └── user_memory.py           # new
└── api/
    └── routes/
        └── chat.py

tests/
└── contract/
    └── test_chat_stream.py
```

**Structure Decision**: Keep the single-project backend layout and add a minimal `src/memory/` persistence module plus targeted `src/agent/` and `src/schemas/` integrations, with contract tests concentrated in the existing chat-stream contract suite.

## Complexity Tracking

No constitution violations requiring exception records.
