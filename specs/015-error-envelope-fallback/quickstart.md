# Quickstart: Error Envelope Fallback Validation

## Prerequisites

- Repository virtual environment available at `.venv`
- Frontend dependencies installed in `frontend/`

## 1. Run Backend Contract Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/contract/test_chat_stream.py
```

Expected outcome:

- Direct-response generation failure emits `direct_response` intent followed by one error event with `ERR-LLM-GENERATION-FAILED` and a non-empty message.
- Policy generation failure emits `policy_question` intent followed by one error event with `ERR-POLICY-GENERATION-FAILED` and a non-empty message.
- Neither generation-failure sequence emits a done event.
- Empty-message exception cases identify their exception type in the error message.

## 2. Build the Frontend

From `frontend/`:

```powershell
npm.cmd run build
```

Expected outcome: TypeScript checking and Vite production build complete without errors.

## 3. Verify Defensive Error Parsing

Exercise the frontend parser with each input below, using the existing frontend test harness or a focused test added for this feature:

| Input | Expected outcome |
|---|---|
| Empty string | Non-empty generic fallback, no throw |
| Whitespace string | Non-empty generic fallback, no throw |
| `{not-json}` | Non-empty generic fallback, no throw |
| `null` | Non-empty generic fallback, no throw |
| `{}` | Non-empty generic fallback, no throw |
| `{"message":""}` | Non-empty generic fallback, no throw |
| Valid Error Envelope | Supplied non-empty message is returned |

## 4. End-to-End Failure Sequences

Start the backend and frontend using their existing development commands. Induce each generation failure through the controlled test path and inspect the stream/UI:

- The interface retains the classified intent followed by one visible error bubble.
- The error bubble is never blank.
- The UI stays interactive and does not crash.
- No completion event is received after the error.

For envelope details, see [error-event-envelope.md](contracts/error-event-envelope.md). For message and fallback rules, see [data-model.md](data-model.md).