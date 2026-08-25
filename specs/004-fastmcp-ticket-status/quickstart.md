# Quickstart: Validate FastMCP Ticket Status Slice

## Prerequisites
- Python 3.11+
- Existing stage-1/stage-2 service baseline present
- Dependencies installed from `requirements.txt`

## Scope for this pass
Add only:
- `src/tools/` for FastMCP `ticket_status_lookup` and mocked in-memory ticket store
- `src/schemas/` additions for `TicketStatusRequest` and `TicketStatusResponse`
- `src/agent/` additions for ticket ID extraction, `check_ticket_status` node, and routing update
- `src/api/routes/chat.py` extension for `tool_call` event with JSON-serialized `TicketStatusResponse` in `data: str`
- Contract test extensions for ticket-status success, missing ID, and unknown ID

Do not add:
- `src/rag/`
- `src/security/`
- password-reset or ticket-creation tools
- any event-envelope schema change beyond current `ChatStreamEvent` contract

## Run service

```bash
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
```

## Validation Scenario A: valid ticket-status lookup
Send message containing an existing ticket ID, for example:
- "status for tkt-1001"

Expected:
1. First event is `intent`
2. Second event is `tool_call` with `data` as JSON string for `TicketStatusResponse`
3. Third event is `token` with natural-language status summary
4. Final event is `done`

## Validation Scenario B: missing ticket ID
Send ticket-status message without ID, for example:
- "what is the status of my ticket"

Expected:
1. First event is `intent`
2. Next event is `error` explaining a ticket ID is required
3. No `tool_call`
4. No `done`

## Validation Scenario C: unknown but well-formed ticket ID
Send message containing unknown ID, for example:
- "status for TKT-9999"

Expected:
1. First event is `intent`
2. Next event is `token` with clear not-found message
3. Final event is `done`
4. No `error`

## Validation Scenario D: non-ticket action_request regression
Send non-ticket action request, for example:
- "please reset my password"

Expected:
1. Existing placeholder path remains unchanged
2. Stream remains `intent` -> `token` -> `done`

## Validation Scenario E: stage-1/stage-2 regression checks
Run pre-existing validation/disconnect and direct-response intent tests.

Expected:
- 422 validation behavior and `ERR-VALIDATION-MISSING-FIELD` shape unchanged
- disconnect behavior unchanged (immediate stop, no retry, no post-disconnect events)
- existing non-ticket and direct-response behavior unaffected

## Run tests

```bash
.\.venv\Scripts\python.exe -m pytest -q tests
```

Expected:
- Existing contract tests remain passing
- New ticket-status contract tests pass for:
  - valid ID success path (`tool_call` + `token` + `done`)
  - missing-ID error path
  - unknown-ID not-found token path

## Verification Record

- Date: 2026-08-25
- Command: `c:\Users\usthe\IT_support_system\.venv\Scripts\python.exe -m pytest -q tests`
- Result: `14 passed, 1 warning`
