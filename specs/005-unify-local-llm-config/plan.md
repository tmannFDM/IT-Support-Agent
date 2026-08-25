# Implementation Plan: Unify Local LLM Configuration

**Branch**: `[005-unify-local-llm-config]` | **Date**: 2026-08-25 | **Spec**: [/specs/005-unify-local-llm-config/spec.md](/specs/005-unify-local-llm-config/spec.md)

**Input**: Feature specification from `/specs/005-unify-local-llm-config/spec.md`

## Summary

Correct a stage-2 configuration inconsistency by consolidating both conversational generation paths
(`direct_response` and `policy_question`) onto one shared local Ollama configuration, removing
active dependency on OpenAI-specific defaults and API-key requirements. The change is intentionally
limited to `src/agent/prompts.py` and `src/agent/nodes.py`, with no schema, routing, RAG module,
or ticket-tool changes and no contract-behavior expansion.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, httpx, pytest

**Storage**: N/A (no new persistence or storage mutations in this pass)

**Testing**: pytest contract suite in `tests/contract/test_chat_stream.py` plus existing tests

**Target Platform**: Local/CI backend runtime on Windows and Linux

**Project Type**: Backend web service

**Performance Goals**:
- Maintain existing stream responsiveness and event ordering.
- Avoid additional path-specific provider setup overhead by unifying configuration.

**Constraints**:
- This pass only touches `src/agent/nodes.py` and `src/agent/prompts.py`.
- Consolidate to one shared local API URL env var and one shared local model env var for both
  direct and policy generation.
- Remove/stop using OpenAI-specific constants and API-key dependency in direct path.
- No new files or modules in source tree.
- No changes to schemas, routing, RAG package internals, or ticket-status tool behavior.
- Existing stream sequence contracts and stage-1/2/3/4 tests must continue passing unchanged.

**Scale/Scope**: Configuration correction affecting two generation call sites in one service.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. This is a contained correction preserving end-to-end behavior.
2. RAG-only policy grounding: PASS. Policy grounding flow remains intact; only provider config is unified.
3. Secure tooling via schema-validated FastMCP: PASS (N/A here; no tool contract changes).
4. Privacy by default: PASS. No new logging or payload-shape expansion is introduced.
5. Prompt-injection resistance and fail-safe outcomes: PASS. Existing policy fail-safe behavior is preserved.
6. Stateful orchestration via LangGraph: PASS. No graph semantics are altered.
7. Schema-first contracts: PASS. No API/schema boundary changes.
8. End-to-end verification gate: PASS with requirement to run existing test suites unchanged.
9. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All gates remain PASS for this correction scope.

## Project Structure

### Documentation (this feature)

```text
specs/005-unify-local-llm-config/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
  └── runtime-config.md
```

### Source Code (repository root)

```text
src/
└── agent/
    ├── prompts.py       # update shared local LLM constants
    └── nodes.py         # update direct path to shared local backend

tests/
└── contract/
    └── test_chat_stream.py  # unchanged expectations; used for verification
```

**Structure Decision**: Keep the existing single-project backend layout and constrain source
changes to `src/agent/prompts.py` and `src/agent/nodes.py` only.

## Complexity Tracking

No constitution violations requiring exception records.
