# Quickstart: Validate Chat Error Handling Baseline

## Prerequisites
- Python 3.11+
- pip

## Build Scope for This Pass
Implement only:
- `src/api/`
- `src/schemas/`
- `tests/`

Do not create in this pass:
- `src/agent/`
- `src/rag/`
- `src/tools/`
- `src/security/`
- `src/observability/`

## Install dependencies

```bash
pip install fastapi uvicorn pydantic pytest httpx
```

## Run service

```bash
uvicorn src.api.main:app --reload --port 8000
```

## Scenario A: `/health` returns 200

```bash
curl -i http://localhost:8000/health
```

Expected:
- HTTP 200
- JSON with non-empty `status` and `version`

## Scenario B: valid stream request

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u-1","session_id":"s-1","message":"hello"}'
```

Expected:
- HTTP 200
- SSE includes one or more `token` events
- Stream ends with terminal `done`

## Scenario C: invalid required fields return 422 + code

Missing/empty/whitespace examples:

```bash
curl -i -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"   ","session_id":"s-1","message":""}'
```

Expected:
- HTTP 422
- JSON contains:
  - `error_code: ERR-VALIDATION-MISSING-FIELD`
  - `message` (human-readable)
  - optional `details` list containing all invalid required fields, each with
    `{ "field": "<name>", "issue": "<reason>" }`

## Scenario D: disconnect handling
1. Start a stream request.
2. Disconnect client before completion (terminate curl or close connection).

Expected:
- Server stops generation immediately
- No retry behavior
- No further events after disconnect

## Run contract tests

```bash
pytest -q tests
```

Expected:
- Contract test for `/chat/stream` success path
- Contract test for `/chat/stream` validation failure path
- Contract test for `/health` 200 response

## Verification Record

- Date: 2026-08-25
- Command: `.\\.venv\\Scripts\\python.exe -m pytest -q tests`
- Result: `6 passed, 1 warning`
