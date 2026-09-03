# Research: Ticket Password Error Envelopes

## Decision: Reuse the existing JSON envelope in `AgentState.error`

**Rationale**: Feature 015 established that error-producing nodes serialize an object with `error_code` and `message` into `AgentState.error`; the existing chat route emits that field directly in an error event. Applying it to the remaining three branches creates compatibility with the frontend without new state, schemas, or events.

**Alternatives considered**:
- Preserve plain strings: rejected because the frontend consumes a JSON error envelope.
- Add a new error field or event: rejected because the existing error state and event fully support the needed payload.

## Decision: Preserve the category-help message verbatim

**Rationale**: The missing-category guidance is already a clear, user-tested explanation of the supported ticket categories. Only its envelope changes.

**Alternatives considered**:
- Replace it with generic failure text: rejected because it loses actionable category guidance.

## Decision: Use path-specific codes and silent-exception fallback

**Rationale**: `ERR-TICKET-CATEGORY-REQUIRED`, `ERR-TICKET-CREATE-FAILED`, and `ERR-PASSWORD-RESET-FAILED` distinguish a validation-style guidance outcome from tool failures. `str(exc)` can be empty, so `{ExceptionType} (no message)` guarantees a usable explanation.

**Alternatives considered**:
- One generic tool error code: rejected because it loses the failure site.
- Empty exception text: rejected because it produces a blank user-visible error.

## Decision: Preserve stream lifecycle by changing node output only

**Rationale**: `generate_chat_events` already emits `intent`, checks `error`, emits an error event, and returns without a tool call or done. Changing only error payloads keeps this behavior unchanged.

**Alternatives considered**:
- Change routing or add a done event: rejected because it modifies established terminal error semantics.