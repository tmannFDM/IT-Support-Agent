# Phase 0 Research: FastMCP Ticket Status Slice

## Decision 1: Tool boundary and execution model
- Decision: Implement ticket status retrieval as a FastMCP tool named `ticket_status_lookup` in `src/tools/`.
- Rationale: Satisfies constitution requirement for secure tooling through explicit tool boundaries and allows later tool expansion without route-layer coupling.
- Alternatives considered:
  - Direct dictionary lookup inside route or node: rejected because it bypasses explicit tool boundary requirement.
  - External database-backed tool: rejected as out of scope for this slice.

## Decision 2: Ticket storage approach
- Decision: Use a small hardcoded in-memory dictionary of sample tickets keyed by normalized `TKT-####` IDs.
- Rationale: Deterministic, test-friendly, and aligned with explicit no-database scope.
- Alternatives considered:
  - File-based fixture store: more I/O complexity with no product gain for this pass.
  - Persistent DB table: outside current slice boundaries.

## Decision 3: Input and output schema contracts
- Decision: Define `TicketStatusRequest` and `TicketStatusResponse` as Pydantic v2 models in `src/schemas/`, reusing the same style as existing schema modules.
- Rationale: Enforces schema-first boundaries and stable contracts for tool and stream payload handling.
- Alternatives considered:
  - TypedDict/dataclass only: weaker runtime validation for API/tool boundaries.
  - Inline dictionaries with ad hoc validation: inconsistent with project contract pattern.

## Decision 4: Ticket ID extraction strategy
- Decision: Extract ticket IDs using case-insensitive regex matching `TKT-\d+`, then normalize to uppercase prefix before lookup.
- Rationale: Directly implements clarified requirement, avoids guessing, and produces deterministic behavior.
- Alternatives considered:
  - Broad alphanumeric extraction: higher false-positive risk and ambiguous behavior.
  - Model-based extraction: unnecessary complexity for deterministic ID pattern.

## Decision 5: Missing and unknown ticket behavior
- Decision: Missing identifiable ticket ID returns `error` event and skips tool invocation; unknown but well-formed ID returns `token` not-found message and `done`.
- Rationale: Matches accepted behavior split between user-correctable input omission and expected business outcome.
- Alternatives considered:
  - Treat unknown IDs as error events: rejected by requirement.
  - Auto-fabricate or infer IDs: rejected for safety and correctness.

## Decision 6: Stream contract compatibility for tool output
- Decision: Keep `ChatStreamEvent` envelope unchanged and encode validated `TicketStatusResponse` as JSON text in `tool_call` event `data` field.
- Rationale: Preserves existing event schema (`data: str`) while delivering structured payload for downstream parsing.
- Alternatives considered:
  - Change `data` type to object: breaks compatibility with existing stream contract and tests.
  - Omit tool payload: reduces observability and fails requirement coverage.

## Decision 7: Agent routing scope
- Decision: Route only ticket-status action requests to a new `check_ticket_status` node; all other action_request messages keep current placeholder path.
- Rationale: Adds targeted capability while protecting prior behavior from broad classification/routing changes.
- Alternatives considered:
  - Route all action_request traffic to tools: out of scope and high regression risk.
  - Replace current action_request path entirely: violates incremental vertical-slice constraint.

## Decision 8: Test strategy and regression assurance
- Decision: Extend contract tests in `tests/contract/test_chat_stream.py` with three ticket-status scenarios and retain existing stage-1/stage-2 assertions.
- Rationale: Keeps behavior verification at external API boundary and satisfies acceptance criteria plus regression guardrails.
- Alternatives considered:
  - Unit tests only: insufficient for stream sequencing contract validation.
  - New integration harness: unnecessary for current service scope.
