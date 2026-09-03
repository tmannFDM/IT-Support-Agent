# Data Model: Error Envelope Fallback

## Error Envelope

**Purpose**: Carry a categorized, user-safe generation failure through the existing error event data field.

| Field | Type | Rules |
|---|---|---|
| `error_code` | string | `ERR-LLM-GENERATION-FAILED` for direct responses or `ERR-POLICY-GENERATION-FAILED` for policy answers |
| `message` | string | Must be non-empty; use the exception message when available, otherwise `{ExceptionType} (no message)` |

**Representation**: The envelope is serialized into the existing `AgentState.error` string and sent as the existing error event's data field. It is not persisted.

## Fallback Error Message

**Purpose**: Keep the chat interface renderable when incoming error-event data cannot be safely interpreted.

| Input condition | Result |
|---|---|
| Empty or whitespace-only data | Generic non-empty fallback message |
| Invalid JSON | Generic non-empty fallback message |
| JSON primitive or array | Generic non-empty fallback message |
| Object missing `message` | Generic non-empty fallback message |
| Object with empty or whitespace-only `message` | Generic non-empty fallback message |
| Object with non-empty string `message` | Supplied message is displayed |

## State Transitions

1. Intent classification emits the existing intent event.
2. Direct or policy response generation raises an exception.
3. The relevant node constructs and serializes its Error Envelope into `error` state.
4. Existing stream handling emits one error event using that serialized payload.
5. The graph ends without a done event.