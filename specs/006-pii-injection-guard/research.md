# Phase 0 Research: PII Redaction and Prompt Injection Guard

## Decision 1: Run guardrails before classification
- Decision: Add a guardrail check step before `classify_intent` in the graph execution path.
- Rationale: Guarantees blocked messages never reach classification, RAG, tools, or LLM calls.
- Alternatives considered:
  - Run checks inside existing classify node: rejected because classification would still be entered.
  - Run checks only in route layer: rejected due to weaker graph-level guarantees.

## Decision 2: Deterministic prompt-injection detector
- Decision: Use case-insensitive, whitespace-normalized keyword/pattern matching for known override phrases.
- Rationale: Meets scope for simple deterministic blocking without adding model variance or extra LLM calls.
- Alternatives considered:
  - LLM-based classifier: rejected as explicitly out of scope.
  - Exact phrase matching without normalization: rejected due to easy bypass risk.

## Decision 3: Visible PII placeholders
- Decision: Replace detected emails with `[REDACTED_EMAIL]` and phone numbers with `[REDACTED_PHONE]`.
- Rationale: Prevents raw PII propagation while preserving user intent context for downstream processing.
- Alternatives considered:
  - Remove PII text completely: rejected because it can degrade intent interpretation and traceability.
  - Hash values: rejected for this slice because visible masking is required and simpler.

## Decision 4: Blocked stream payload format
- Decision: Keep existing `error` event envelope and encode blocked details as JSON string in `data`, including `error_code` and `message`.
- Rationale: Preserves schema compatibility while delivering machine-readable blocked codes.
- Alternatives considered:
  - Add new event fields/schema: rejected due to regression risk and unnecessary contract expansion.

## Decision 5: Fixed blocked message text
- Decision: Use exact message `Request blocked for safety.` for all blocked prompt-injection results.
- Rationale: Deterministic behavior improves client handling and avoids revealing detection logic.
- Alternatives considered:
  - Pattern-specific messages: rejected because they can teach evasion patterns.

## Decision 6: Regression preservation boundary
- Decision: Keep existing stage 1-4 validation, error-code behavior, disconnect handling, and intent/RAG/tool logic unchanged except for earlier guardrail insertion.
- Rationale: Constrains blast radius and maintains established contracts.
- Alternatives considered:
  - Broader refactor of intent and route logic: rejected as out of scope for this slice.
