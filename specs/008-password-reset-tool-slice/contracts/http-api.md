# HTTP Contract: Password Reset Tool Slice

## Endpoint: POST /chat/stream

### Request body
- Unchanged envelope from existing contract.

### Stream envelope
- Unchanged event wrapper:

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Password-reset routing contract
- Password-reset-specific action requests route to check_password_reset handling.
- Ticket-status routing remains distinct and unchanged.
- Generic action_request placeholder is not used for password-reset-specific requests.

## Password reset success contract
1. First event: intent
2. Second event: tool_call containing PasswordResetResponse with:
   - status = reset_issued
   - temporary_password_note = "A temporary password has been issued and will be required to be changed on next login."
   - escalation_reason = null
3. Third event: token confirmation message
4. Final event: done

## Suspicious escalation contract
- Conditions:
  - invalid employee ID (fails EMP-\d{4})
  - urgency pressure language
  - vague or missing reason (fixed generic phrase list)
- Output sequence:
  1. intent
  2. token escalation message
  3. done
- Escalation reason field values allowed:
  - vague_reason
  - urgency_pressure
  - invalid_employee_id
- Multi-signal precedence:
  - invalid_employee_id > urgency_pressure > vague_reason

## Unexpected tool failure contract
- If password_reset tool raises unexpected failure:
  1. intent
  2. error
  3. no done

## Regression contract guarantees
- No changes to:
  - ticket_status_lookup tool behavior
  - RAG policy-answer flow
  - stage-5 guardrail blocked behavior
  - existing non-password action_request contracts
