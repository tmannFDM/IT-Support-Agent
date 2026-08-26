# Quickstart: Validate Ticket Creation Tool Slice

## Prerequisites
- Python 3.11+
- Virtual environment available at `./.venv`
- Existing chat stream endpoint and prior slices operational

## Scope for this pass
Add only:
- `src/tools/` additions for `create_ticket` and shared-store insertion
- `src/schemas/` additions for `TicketCreateRequest` and `TicketCreateResponse`
- `src/agent/` additions for create-ticket inference/routing behavior
- contract tests covering new creation scenarios and no-regression checks

Do not modify:
- existing ticket-status lookup tool internal logic
- password reset tool logic
- RAG pipeline
- guardrail logic beyond routing hooks needed for this slice

## Validation Scenario A: Categorizable create request succeeds
Input message example:
- "Please create a ticket for VPN connection failing for remote login."

Expected:
1. `intent` = `action_request`
2. `tool_call` payload is valid `TicketCreateResponse`
3. `category` inferred as `VPN`
4. `priority` inferred from severity keywords or defaults to `medium`
5. `ticket_id` is new `TKT-####` and non-colliding
6. `token` includes the new ticket_id
7. `done` emitted

## Validation Scenario B: Uncategorizable create request fails safe
Input message example:
- "Create a ticket for my issue"

Expected:
1. `intent` = `action_request`
2. `error` event requests more detail
3. no `tool_call` for creation
4. no new ticket inserted

## Validation Scenario C: Newly created ID is immediately lookupable
Flow:
1. create ticket and capture `ticket_id`
2. submit ticket-status lookup request with that ID

Expected:
- existing ticket-status lookup path returns the newly created ticket without lookup logic changes

## Validation Scenario D: Mixed create/status message prefers status lookup
Input message example:
- "Create a ticket update for TKT-1002"

Expected:
- route follows existing status-lookup behavior (valid ticket ID precedence)
- no duplicate ticket is created from this mixed-intent message

## Validation Scenario E: Existing stage 1-6 behavior unchanged
Run direct-response, policy-question, password-reset, and guardrail checks to confirm prior expectations still pass.

## Regression commands
```bash
./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py
./.venv/Scripts/python.exe -m pytest -q tests
```

Expected:
- new ticket-creation scenarios pass
- previously passing stage 1-6 tests remain passing

## Validation Results (2026-08-26)

- `./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py` -> 30 passed, 2 warnings
- `./.venv/Scripts/python.exe -m pytest -q tests` -> 29 passed, 2 warnings
