# Data Model: Password Reset Escalation ToolCall Fix

## Entity: EscalatedPasswordResetResponse (existing schema instance)
- Purpose: Structured data payload emitted in tool_call for escalation outcomes.
- Fields:
  - employee_id: str
  - status: Literal["escalated"]
  - temporary_password_note: str
  - escalation_reason: Literal["invalid_employee_id", "urgency_pressure", "vague_reason"]
- Validation rules:
  - Uses existing PasswordResetResponse schema without modification.
  - escalation_reason remains selected by existing precedence rules.

## Entity: EscalationUserTokenMessage
- Purpose: Human-readable follow-up token after structured escalation tool_call.
- Fields:
  - message_text: str
- Validation rules:
  - Must not contain raw field identifiers (for example escalation_reason), underscore identifiers, or key=value fragments.
  - Must remain explanatory and user-facing.

## Entity: EscalationStreamEventOrder
- Purpose: Contracted ordering for escalated password-reset outcomes.
- Sequence:
  - intent
  - tool_call (EscalatedPasswordResetResponse JSON)
  - token (clean human-readable escalation text)
  - done
- Validation rules:
  - Success path remains unchanged.
  - Unexpected runtime failure remains intent -> error -> no done.
