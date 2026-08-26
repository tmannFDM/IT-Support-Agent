# Implementation Plan: Injection Pattern Expansion

**Branch**: `[007-injection-pattern-expansion]` | **Date**: 2026-08-26 | **Spec**: [/specs/007-injection-pattern-expansion/spec.md](/specs/007-injection-pattern-expansion/spec.md)

**Input**: Feature specification from `/specs/007-injection-pattern-expansion/spec.md`

## Summary

Expand the existing static `INJECTION_PATTERNS` list in `src/security/injection.py`
with additional dismissal, role-override, and prompt-extraction phrase variants while
preserving all current detection mechanics and blocked-response semantics. Add one
targeted regression test for `forget everything you were told before this message`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph, pytest

**Storage**: N/A

**Testing**: pytest contract tests, primarily `tests/contract/test_chat_stream.py`

**Target Platform**: Backend service on local and CI environments

**Project Type**: Backend web service

**Performance Goals**:
- Preserve current detection latency characteristics by changing phrase data only.
- Maintain existing blocked-response behavior with no additional processing branches.

**Constraints**:
- This pass only touches `src/security/injection.py` for phrase-list data updates.
- No new source files or modules.
- No changes to detection logic, normalization, guardrail routing, response shape, or event handling.
- Preserve all stage behavior outside expanded phrase coverage.
- Add one new test case for phrase `forget everything you were told before this message`.

**Scale/Scope**: Single-file pattern-list expansion and one targeted contract-test addition.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:
1. Vertical slice first: PASS. This is a bounded improvement to existing guardrail behavior.
2. RAG-only policy grounding: PASS. No RAG behavior changes.
3. Secure tooling via schema-validated FastMCP: PASS. Tooling layer unchanged.
4. Privacy by default: PASS. Existing redaction behavior unchanged; detection coverage improves safety.
5. Prompt injection resistance and fail-safe outcomes: PASS. Improves phrase coverage while preserving fail-safe path.
6. Stateful orchestration and data contracts: PASS. No graph or schema changes.
7. End-to-end verification gate: PASS with contract/full-suite test validation.
8. Honest Copilot documentation: PASS as process requirement.

Post-Phase 1 design re-check:
All gates remain PASS for this scoped feature.

## Project Structure

### Documentation (this feature)

```text
specs/007-injection-pattern-expansion/
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
└── security/
    └── injection.py      # expand INJECTION_PATTERNS list only

tests/
└── contract/
    └── test_chat_stream.py   # add one missed-phrase test case
```

**Structure Decision**: Keep existing architecture intact and constrain implementation to
data-only phrase additions in `src/security/injection.py` plus one contract test addition.

## Complexity Tracking

No constitution violations requiring exception records.
