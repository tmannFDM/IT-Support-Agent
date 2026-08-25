# Quickstart: Validate Chat Stream Vertical Slice

## Prerequisites
- Python 3.11+
- pip

## Scope for this pass
Only these code areas are implemented:
- `src/api/`
- `src/schemas/`
- `tests/`

Not implemented in this pass:
- `src/agent/`, `src/rag/`, `src/tools/`, `src/security/`, `src/observability/`

## Setup
1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies (minimum expected):

```bash
pip install fastapi uvicorn pydantic pytest httpx
```

## Run the service
From repository root:

```bash
uvicorn src.api.main:app --reload --port 8000
```

## Validation Scenario A: Health endpoint

```bash
curl -i http://localhost:8000/health
```

Expected outcome:
- HTTP `200`
- JSON includes non-empty `status` and `version`

## Validation Scenario B: Valid stream request

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u-123","session_id":"s-123","message":"hello"}'
```

Expected outcome:
- HTTP `200`
- SSE output includes at least one event with `event_type: token`
- SSE output ends with exactly one event with `event_type: done`

Contract reference: [contracts/http-api.md](contracts/http-api.md)

## Validation Scenario C: Missing or empty field
Missing `message` example:

```bash
curl -i -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u-123","session_id":"s-123"}'
```

Empty `message` example:

```bash
curl -i -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u-123","session_id":"s-123","message":""}'
```

Expected outcome for both:
- Validation error response
- Includes `error_code: ERR-VALIDATION-MISSING-FIELD`

## Test execution

```bash
pytest -q tests
```

Expected outcome:
- Contract test verifies valid stream path reaches `done`
- Contract test verifies missing/empty fields surface `ERR-VALIDATION-MISSING-FIELD`
- Contract test verifies `/health` returns `200`
