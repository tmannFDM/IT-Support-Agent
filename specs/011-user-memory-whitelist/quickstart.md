# Quickstart: Validate Long-Term User Memory Whitelist

## Prerequisites
- Python 3.11+
- Existing stage 1-7 functionality passing
- Writable local filesystem for JSON memory file

## Scope for this pass
Add only:
- `src/memory/` JSON-backed store module
- `src/schemas/` user memory facts schema
- `src/agent/` extraction and context wiring
- contract tests in `tests/contract/test_chat_stream.py`

Do not add or modify:
- Arize Phoenix instrumentation
- Promptfoo evaluation
- React frontend
- Ticket/password-reset/RAG/guardrail semantics beyond minimal memory read/write wiring

## Validation Scenario A: Fact persists and is reused across sessions
1. Send request with user_id U1/session_id S1 stating a valid fact (for example preferred device type).
2. Send second request with user_id U1/session_id S2.

Expected:
- Fact is persisted after first request.
- Second request can access that fact by user_id despite new session_id.

## Validation Scenario B: Mixed valid and non-whitelisted candidates
1. Send request with one valid whitelist fact and one non-whitelisted candidate.

Expected:
- Valid whitelist fact is stored.
- Non-whitelisted candidate is ignored.
- Response path still completes normally.

## Validation Scenario C: Restart persistence
1. Store one or more whitelist facts for user_id U2.
2. Simulate restart by reinitializing/reloading memory store module.
3. Send follow-up request for user_id U2.

Expected:
- Stored facts remain available after restart simulation.

## Validation Scenario D: No-memory-content behavior parity
1. Send request with no memory-relevant content for user with stored facts.
2. Send equivalent request for user with no stored facts.

Expected:
- Both requests complete normally with expected stage behavior.
- No new memory fields are created from irrelevant content.

## Regression commands
```bash
./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py
./.venv/Scripts/python.exe -m pytest -q tests
```

Expected:
- New memory-whitelist contract scenarios pass.
- Existing stage 1-7 tests remain passing.

## Validation Results (2026-08-26)

- `./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py` -> 33 passed, 2 warnings
- `./.venv/Scripts/python.exe -m pytest -q tests` -> 34 passed, 2 warnings
