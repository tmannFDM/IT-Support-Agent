# Phase 0 Research: Ticket Creation Tool Slice

## Decision 1: Add a schema-validated FastMCP create_ticket tool with shared store write-through
- Decision: Implement `create_ticket` as a FastMCP tool in `src/tools/` with Pydantic request/response validation and insertion into the same in-memory ticket store used by ticket-status lookup.
- Rationale: Satisfies constitution requirement for schema-validated tool execution and guarantees immediate lookup compatibility for newly created tickets.
- Alternatives considered:
  - Build ticket creation directly in agent node without a tool: rejected because it bypasses the required tool contract boundary.
  - Create a separate store for ticket creation: rejected because it breaks immediate status lookup consistency.

## Decision 2: Ticket ID generation uses monotonic increment with collision scan
- Decision: Generate IDs in `TKT-####` format by deriving next numeric value from existing store IDs, with floor above seeded `TKT-1001` range, then increment until an unused ID is found.
- Rationale: Deterministic, testable, and robust against collisions while matching clarified behavior.
- Alternatives considered:
  - Random ID generation: rejected due to non-determinism and flaky tests.
  - Fail on first collision: rejected because it degrades UX and is unnecessary for in-memory mocked flow.

## Decision 3: Deterministic category inference via keyword mapping with fixed precedence
- Decision: Use keyword detection for categories with precedence `Access > VPN > Password > Hardware > Software` when multiple categories match.
- Rationale: Resolves mixed-category ambiguity deterministically and aligns with approved clarification.
- Alternatives considered:
  - First match in message order: rejected because punctuation/ordering would change output unexpectedly.
  - LLM categorization: rejected by explicit out-of-scope and determinism constraints.

## Decision 4: Priority inference by severity keywords with default medium
- Decision: Infer priority from severity language; if no severity signals are present and category is clear, set priority to `medium`.
- Rationale: Provides predictable output for routine requests and matches approved clarification.
- Alternatives considered:
  - Default low: rejected because it risks under-prioritizing actionable incidents.
  - Require explicit priority from user: rejected because it adds friction and unnecessary failures.

## Decision 5: Mixed-intent routing prioritizes valid ticket ID status lookup path
- Decision: In action-request routing, if a valid ticket ID pattern is present in the message, route to existing status-lookup node/path first; otherwise evaluate create-ticket cues.
- Rationale: Avoids accidental ticket creation when user likely references an existing ticket and matches clarified precedence.
- Alternatives considered:
  - Always prioritize create cues: rejected because it can mis-handle lookup-first user intent.
  - Return ambiguity error for mixed intent: rejected because deterministic precedence is preferred.

## Decision 6: Error handling for uncategorizable ticket creation remains fail-safe
- Decision: If no category keyword match is found for a creation request, return an `error` event and do not emit `tool_call` or create a ticket.
- Rationale: Upholds fail-safe behavior from constitution and explicit spec requirements.
- Alternatives considered:
  - Guess category from closest match: rejected due to misclassification risk.
  - Create ticket with category `unknown`: rejected because it breaks strict category contract literals.

## Decision 7: Contract-test expansion locks stream order and no-regression guarantees
- Decision: Extend `tests/contract/test_chat_stream.py` with ticket-creation success/failure/lookup-precedence scenarios while preserving existing stage 1-6 assertions.
- Rationale: Provides automated proof that only intended behavior changed.
- Alternatives considered:
  - Rely on manual validation only: rejected due to regression risk.
