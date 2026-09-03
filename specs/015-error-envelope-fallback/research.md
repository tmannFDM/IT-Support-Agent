# Research: Error Envelope Fallback

## Decision: Reuse the existing serialized error-envelope convention

**Rationale**: `guardrail_check_node` already stores a JSON-serialized object containing `error_code` and `message` in `AgentState.error`. The stream layer already places that state field in the error event data. Applying this pattern to the two generation-failure handlers corrects the inconsistency without changing graph routing, event types, or transport.

**Alternatives considered**:
- Add a new error event type: rejected because the current error event carries the required information.
- Add a new state field or schema: rejected because `AgentState.error` is the established serialized stream payload boundary.

## Decision: Use explicit failure codes for each generation path

**Rationale**: `ERR-LLM-GENERATION-FAILED` identifies direct-response generation failures, while `ERR-POLICY-GENERATION-FAILED` identifies policy-answer generation failures. This makes operational diagnosis possible without exposing stack traces to the user.

**Alternatives considered**:
- A single generic generation error code: rejected because it cannot distinguish direct and policy failure sites.

## Decision: Build a non-empty exception message before envelope serialization

**Rationale**: `str(exc)` may be empty. The fallback `{ExceptionType} (no message)` guarantees that the user-visible error field cannot be blank while retaining useful diagnostic context.

**Alternatives considered**:
- Emit an empty message: rejected by the feature requirements and causes blank error UI.
- Expose a traceback: rejected because it leaks internal detail and violates safe error rendering expectations.

## Decision: Keep frontend fallback parsing defensive

**Rationale**: The frontend consumes a backend stream boundary that may contain legacy, malformed, or empty event data. `parseErrorPayload` must treat parse failures, JSON primitives, missing messages, and empty messages as invalid and return the existing generic fallback.

**Alternatives considered**:
- Throw on invalid payload: rejected because it can crash the chat exactly when reporting a failure.
- Render raw data: rejected because it can expose untrusted or internal error content.

## Decision: Preserve current event order and graph termination

**Rationale**: The graph terminates after either affected node. The stream's existing state-to-event handling emits the classified intent and then the error field, without a `done` event. Error formatting alone must not change this lifecycle.

**Alternatives considered**:
- Emit `done` after error: rejected because existing failure semantics and frontend behavior expect error to be terminal.