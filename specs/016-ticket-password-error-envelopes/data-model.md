# Data Model: Ticket Password Error Envelopes

## Error Envelope

**Purpose**: Convey ticket-creation and password-reset errors through the existing error event data field in a form the frontend can parse safely.

| Field | Type | Validation |
|---|---|---|
| `error_code` | string | One of the three documented failure categories for this feature |
| `message` | string | Non-empty; exception failures use original text or `{ExceptionType} (no message)` |

**Representation**: A JSON-serialized Error Envelope stored in the existing `AgentState.error` field. It is sent unchanged in the existing stream error event.

## Error Categories

| Source | Error code | Message source |
|---|---|---|
| Ticket request lacks a recognized category | `ERR-TICKET-CATEGORY-REQUIRED` | Current category-guidance text, unchanged |
| Ticket creation tool raises | `ERR-TICKET-CREATE-FAILED` | Exception text, or no-message fallback |
| Password reset tool raises | `ERR-PASSWORD-RESET-FAILED` | Exception text, or no-message fallback |

## State Transitions

1. Existing intent classification sets `action_request`.
2. Existing node detects missing ticket category or catches the relevant tool exception.
3. The node serializes its Error Envelope into `error` state.
4. Existing route emits `intent` then `error` and ends without tool-call or done events.

Ticket category/priority inference, tool invocation, ticket creation success, password reset success, and escalation transitions are unchanged.