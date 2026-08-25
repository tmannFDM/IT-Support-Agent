# Phase 0 Research: LangGraph Intent Slice

## Decision 1: Orchestration model
- Decision: Use a LangGraph state graph with explicit classify_intent and generate_response nodes.
- Rationale: Meets slice objective for stateful routing and keeps flow transitions explicit and testable.
- Alternatives considered:
  - In-route imperative branching: faster to write but less observable and less extensible for later slices.
  - Full multi-agent framework: unnecessary complexity for current scope.

## Decision 2: Agent state contract
- Decision: Define AgentState with at least user_id, session_id, message, intent, response.
- Rationale: Satisfies required minimum state and provides forward-compatible structure for later nodes.
- Alternatives considered:
  - Minimal ephemeral locals only: weak traceability and poor extensibility.
  - Overly broad state now: introduces premature complexity.

## Decision 3: Intent classification set
- Decision: Classify into exactly five intents: policy_question, action_request, direct_response, escalation, blocked.
- Rationale: Required by spec and sufficient to separate current capabilities from placeholders.
- Alternatives considered:
  - Binary direct/non-direct only: insufficient for future routing and acceptance requirements.

## Decision 4: Intent visibility encoding
- Decision: Extend ChatStreamEvent.event_type with intent and emit intent event first in stream sequence.
- Rationale: Deterministic acceptance verification at API boundary without depending on logs.
- Alternatives considered:
  - Logs-only visibility: harder to test consistently.
  - Reusing tool_call event: rejected by accepted clarification in this feature.

## Decision 5: Non-direct and failure behavior
- Decision: Non-direct intents emit placeholder text `This type of request isn't supported yet.` with success sequence intent -> token(s) -> done.
- Decision: direct_response LLM failure emits intent -> error and terminates without done.
- Rationale: Matches clarifications and keeps termination behavior explicit.
- Alternatives considered:
  - Placeholder fallback on generation failure: explicitly rejected.
  - Always emitting done after error: explicitly rejected.

## Decision 6: Scope controls
- Decision: Limit new code to src/agent plus targeted schema/API/test updates; do not create rag/tools/security/observability modules.
- Rationale: Preserves vertical-slice discipline and avoids out-of-scope expansion.
- Alternatives considered:
  - Stub future modules now: adds noise and maintenance burden.

## Clarifications Resolved
- Intent visibility is in stream via dedicated intent event before token events.
- Non-direct intents use exact placeholder text.
- ChatStreamEvent includes intent in event_type.
- direct_response LLM failure emits error and stops without done.
- Success sequence is intent -> token(s) -> done.
