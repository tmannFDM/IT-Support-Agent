# Data Model: Password Reset Tool Slice

## Entity: PasswordResetRequest
- Purpose: Validated input payload for password reset processing.
- Fields:
  - employee_id: str
  - reason: str
- Validation rules:
  - employee_id must match pattern EMP- followed by exactly 4 digits.
  - reason must be present; additional suspicion checks evaluate reason vagueness and urgency pressure.

## Entity: PasswordResetResponse
- Purpose: Validated output payload for password reset outcomes.
- Fields:
  - employee_id: str
  - status: Literal["reset_issued", "escalated"]
  - temporary_password_note: str
  - escalation_reason: Literal["vague_reason", "urgency_pressure", "invalid_employee_id"] | None
- Validation rules:
  - escalation_reason is required when status is escalated and must follow single-reason precedence.
  - temporary_password_note must never include an actual generated password value.

## Entity: PasswordResetSuspicionAssessment
- Purpose: Internal decision artifact in check_password_reset node.
- Fields:
  - invalid_employee_id: bool
  - urgency_pressure: bool
  - vague_reason: bool
  - selected_escalation_reason: Literal["vague_reason", "urgency_pressure", "invalid_employee_id"] | None
- Validation rules:
  - selected_escalation_reason uses precedence invalid_employee_id > urgency_pressure > vague_reason.
  - assessment occurs before any tool execution.

## Entity: PasswordResetToolResult
- Purpose: Tool execution result represented in stream tool_call data.
- Fields:
  - employee_id: str
  - status: Literal["reset_issued", "escalated"]
  - temporary_password_note: str
  - escalation_reason: Literal["vague_reason", "urgency_pressure", "invalid_employee_id"] | None
- Validation rules:
  - success path emits status reset_issued with fixed note.
  - suspicious requests bypass tool and return token escalation path.

## Entity: PasswordResetStreamOutcome
- Purpose: Stream contract for password-reset-specific action requests.
- States:
  - success: intent -> tool_call -> token -> done
  - suspicious escalation: intent -> token -> done
  - unexpected tool failure: intent -> error (no done)
- Validation rules:
  - Existing stage 1-5 stream behavior remains unchanged for non-password-reset requests.
