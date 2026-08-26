# Quickstart: Validate Password Reset Escalation ToolCall Fix

## Prerequisites
- Python 3.11+
- Existing password-reset slice (feature 008) implemented
- Existing contract suite available

## Scope for this pass
Touch only:
- src/agent/nodes.py
- src/api/routes/chat.py (only if needed for escalation tool_call emission)

Do not change:
- schemas
- success-path reset behavior
- ticket-status routing
- RAG pipeline
- stage-5 guardrail logic

## Validation Scenario A: Invalid ID escalation emits tool_call then token
Input: password-reset request with invalid employee ID.
Expected sequence:
1. intent
2. tool_call (status=escalated, escalation_reason=invalid_employee_id)
3. token (clean human-readable text)
4. done

## Validation Scenario B: Urgency-pressure escalation emits tool_call then token
Input: valid employee ID plus urgency language.
Expected sequence:
1. intent
2. tool_call (status=escalated, escalation_reason=urgency_pressure)
3. token (clean human-readable text)
4. done

## Validation Scenario C: Vague-reason escalation emits tool_call then token
Input: valid employee ID with vague fixed-list reason and no urgency.
Expected sequence:
1. intent
2. tool_call (status=escalated, escalation_reason=vague_reason)
3. token (clean human-readable text)
4. done

## Validation Scenario D: Success path unchanged
Input: valid password-reset request with specific reason.
Expected sequence remains:
1. intent
2. tool_call (status=reset_issued)
3. token
4. done

## Regression commands
```bash
./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py
./.venv/Scripts/python.exe -m pytest -q tests
```

Expected:
- four password-reset scenarios pass with escalation order assertions updated
- prior stage behavior remains unchanged
