# Quickstart: Validate In-Session Conversation History Window

## Prerequisites
- Python 3.11+
- Existing backend dependencies installed from `requirements.txt`
- Existing stage 1-8 tests passing baseline

## Scope for this pass
Add only:
- `src/agent/` session-history module and prompt wiring
- `tests/contract/test_chat_stream.py` additions for history behavior

Do not modify:
- Long-term user memory module semantics in `src/memory/`
- Ticket/password-reset/ticket-creation tool logic
- RAG retrieval behavior
- Guardrail injection/redaction behavior beyond using already-redacted current message for history storage

## Validation Scenario A: Same-session follow-up uses prior context
1. Start session `S1` for user `U1` and send a policy/direct question with clear topic (for example VPN policy).
2. Send a follow-up in the same session (`S1`) that omits the original topic (for example "what about for contractors?").
3. In test, monkeypatch the direct/policy LLM call path to capture the constructed `messages` list.

Expected:
- Second request LLM payload includes prior turn messages from session `S1` before the current user message.
- Follow-up context can be interpreted from prior turn payload without user restating topic.

## Validation Scenario B: New session isolation with same user
1. Seed session `S1` for user `U2` with at least one completed exchange.
2. Send first request in new session `S2` for same user `U2`.
3. Capture LLM payload messages for session `S2`.

Expected:
- `S2` payload contains no prior-turn history from `S1`.
- Session history remains keyed by `session_id`, not `user_id`.

## Validation Scenario C: Sliding window eviction correctness
1. For one session `S3`, complete six direct/policy exchanges sequentially.
2. Capture history used for the sixth request prompt.

Expected:
- Exactly five most recent prior exchanges are retained.
- Oldest (first) exchange is absent.
- Newest exchanges remain present in order.

## Validation Scenario D: Tool paths unaffected by history presence
1. Seed history in session `S4` with one or more non-tool exchanges.
2. Send ticket status, password reset, and ticket creation requests (existing contract patterns).
3. Compare behavior with/without seeded history.

Expected:
- Intent routing/extraction behavior remains current-message-only.
- Event sequencing and tool_call payload behavior remain unchanged.

## Suggested test execution commands
```bash
./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py
./.venv/Scripts/python.exe -m pytest -q tests
```

Expected:
- New history contract tests pass.
- Existing stage 1-8 behavior remains passing, including tool-invoking paths.

## Validation Results (2026-08-31)

- `./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py` -> 40 passed, 2 warnings
- `./.venv/Scripts/python.exe -m pytest -q tests` -> 41 passed, 2 warnings
- Verified scenarios in this run:
	- Same-session prior-turn context is injected for direct and policy LLM calls.
	- New session_id starts with empty short-term history even with same user_id.
	- Sixth completed turn evicts oldest entry in a 5-turn window.
	- Ticket status, password reset, and ticket creation paths remain history-independent.
