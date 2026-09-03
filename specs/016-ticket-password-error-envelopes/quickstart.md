# Quickstart: Ticket Password Error Envelopes

## Prerequisites

- Repository virtual environment available at `.venv`
- Existing backend contract-test dependencies installed

## 1. Run Focused Contract Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/contract/test_chat_stream.py
```

Expected outcomes:

- A category-less ticket request returns an `ERR-TICKET-CATEGORY-REQUIRED` envelope containing the current category guidance.
- Simulated ticket-create and password-reset tool exceptions return their documented error codes and non-empty messages.
- Silent exceptions include their exception type name and a no-message indication.
- All three paths retain `action_request`, then `error`, with no tool call or done.
- Existing ticket success and password-reset success/escalation cases pass unchanged.

## 2. Run Full Regression Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

Expected outcome: all tests pass.

## 3. Inspect Stream Error Payloads

For each scenario, inspect the error event data and parse it as JSON. It must contain `error_code` and a non-empty `message`; never render or depend on the raw plain-text payload.

Envelope details are in [ticket-password-error-envelope.md](contracts/ticket-password-error-envelope.md); state transitions are in [data-model.md](data-model.md).