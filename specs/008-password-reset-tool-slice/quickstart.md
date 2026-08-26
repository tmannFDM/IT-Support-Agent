# Quickstart: Validate Password Reset Tool Slice

## Prerequisites
- Python 3.11+
- Existing backend environment and dependencies installed
- Existing stage 1-5 behavior and tests available

## Implementation scope for this pass
Add only:
- src/tools password_reset FastMCP tool with mocked in-memory behavior
- src/schemas PasswordResetRequest and PasswordResetResponse
- src/agent check_password_reset node and routing updates for password-reset-specific action requests
- tests for password-reset success/escalation plus stage 1-5 regression safety

Do not modify:
- ticket_status_lookup tool behavior
- RAG pipeline behavior
- stage-5 guardrail logic beyond routing into password-reset node
- ticket creation tooling or long-term memory features

## Validation Scenario A: Valid reset request succeeds
Input message includes:
- password reset intent
- valid employee ID matching EMP-\d{4}
- specific non-vague reason

Expected stream:
1. intent
2. tool_call with status reset_issued and fixed temporary-password note
3. token confirmation
4. done

## Validation Scenario B: Invalid employee ID precedence
Input message includes:
- password reset intent
- malformed employee ID
- other suspicious signals may also be present

Expected stream:
1. intent
2. token escalation
3. done
And escalation_reason resolves to invalid_employee_id due to precedence.

## Validation Scenario C: Urgency pressure escalation
Input message includes:
- valid employee ID
- urgency pressure language
- non-vague reason otherwise

Expected stream:
1. intent
2. token escalation with escalation_reason urgency_pressure
3. done

## Validation Scenario D: Vague reason escalation
Input message includes:
- valid employee ID
- no urgency language
- reason missing or in fixed vague phrase list

Expected stream:
1. intent
2. token escalation with escalation_reason vague_reason
3. done

## Regression validation
Run targeted contract tests:

```bash
./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py
```

Run full suite:

```bash
./.venv/Scripts/python.exe -m pytest -q tests
```

Expected:
- New password-reset cases pass.
- Existing stage 1-5 tests remain unchanged and passing.
