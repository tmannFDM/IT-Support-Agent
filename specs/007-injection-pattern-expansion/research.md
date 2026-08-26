# Phase 0 Research: Injection Pattern Expansion

## Decision 1: Data-only pattern list expansion
- Decision: Expand `INJECTION_PATTERNS` entries only, without modifying detection code paths.
- Rationale: The request explicitly constrains this pass to phrase-data changes and preserves stable behavior.
- Alternatives considered:
  - Introduce regex-based advanced matching logic: rejected as out of scope.
  - Add per-category matching branches: rejected because it alters detection mechanism.

## Decision 2: Broaden dismissal and role-override coverage
- Decision: Add variants for dismissing prior instructions, role/persona override prompts, and prompt extraction requests.
- Rationale: These phrase families represent common low-effort injection attempts that should trigger existing block behavior.
- Alternatives considered:
  - Minimal one-phrase update only: rejected because it misses the requested variant coverage.

## Decision 3: Preserve response and routing contracts
- Decision: Keep blocked response shape, routing behavior, and event sequencing unchanged.
- Rationale: Existing contracts are already validated and this feature is intended to increase coverage only.
- Alternatives considered:
  - Add new error metadata fields: rejected to avoid contract drift.

## Decision 4: Add one targeted regression case
- Decision: Add a contract test for `forget everything you were told before this message`.
- Rationale: Explicitly guards the previously missed phrase without expanding test scope unnecessarily.
- Alternatives considered:
  - Broad new test matrix: rejected for this focused pass.
