# Phase 0 Research: Unify Local LLM Configuration

## Decision 1: Shared local provider configuration
- Decision: Use one shared local LLM configuration (single API URL env var and single model env var) for both `direct_response` and `policy_question` generation paths.
- Rationale: Removes configuration drift and aligns runtime behavior with project-local execution scope.
- Alternatives considered:
  - Keep separate provider configs per path: rejected due to mismatch risk and operator confusion.
  - Keep shared model but separate endpoint env vars: rejected as unnecessary duplication.

## Decision 2: Remove active OpenAI default dependency
- Decision: Stop using OpenAI-specific defaults and API-key-gated behavior in the direct path.
- Rationale: The system is scoped to run fully local; external-provider defaults are misleading and brittle in this environment.
- Alternatives considered:
  - Preserve OpenAI fallback behavior behind conditional logic: rejected because it violates local-only operational intent for this pass.

## Decision 3: Preserve stream contracts unchanged
- Decision: Do not change event sequencing or payload schema for success/error in either path.
- Rationale: This is a correction pass; behavior contracts are already validated and must remain stable.
- Alternatives considered:
  - Introduce new event markers for backend provenance: rejected as out of scope and unnecessary for correction.

## Decision 4: Limit implementation surface
- Decision: Restrict code edits to `src/agent/prompts.py` and `src/agent/nodes.py`.
- Rationale: Matches requested scope boundary and minimizes regression risk.
- Alternatives considered:
  - Add shared config helper module: rejected because no new modules are allowed in this pass.
