# Quickstart: Validate LangGraph Intent Slice

## Prerequisites
- Python 3.11+
- Existing stage-1 service baseline present
- Configured LLM provider credentials for direct_response tests

## Scope for this pass
Add only:
- src/agent/ (state, graph, classify_intent node, generate_response node, prompts)
- src/schemas/chat.py update (intent event_type)
- src/api/routes/chat.py routing through graph
- tests updates for new intent-driven streaming behavior

Do not add:
- src/rag/
- src/tools/
- src/security/
- src/observability/

## Run service

```bash
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
```

## Validation Scenario A: direct_response success path
Send a direct-response-style message (for example: "what can you do?").

Expected:
1. Stream first event_type is intent
2. Intent value indicates direct_response
3. One or more token events follow
4. Final done event is present exactly once

## Validation Scenario B: non-direct placeholder path
Send messages classifiable as policy_question, action_request, escalation, and blocked.

Expected per request:
1. intent event first with corresponding label
2. token content returns exact placeholder text:
   This type of request isn't supported yet.
3. done event terminates stream

## Validation Scenario C: direct_response generation failure path
Force or simulate LLM failure for a direct_response request.

Expected:
1. intent event first
2. error event emitted
3. stream terminates without done

## Validation Scenario D: stage-1 regression checks
Run previous validation and disconnect tests unchanged.

Expected:
- 422 validation behavior and ERR-VALIDATION-MISSING-FIELD shape unchanged
- disconnect handling unchanged (immediate stop, no retry, no further events)

## Run tests

```bash
.\.venv\Scripts\python.exe -m pytest -q tests
```

Expected:
- Existing stage-1 tests still pass
- New contract tests for direct_response success, non-direct placeholder, and generation failure pass

## Verification Record

- Date: 2026-08-25
- Command: `c:\Users\usthe\IT_support_system\.venv\Scripts\python.exe -m pytest -q tests`
- Result: `11 passed, 1 warning`
