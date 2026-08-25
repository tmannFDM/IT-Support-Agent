# IT Support System MVP Backend Slice

This repository contains a minimal FastAPI vertical slice for chat streaming and baseline error handling.

## Endpoints

- `POST /chat/stream`
- `GET /health`

## Run

```bash
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
```

## Usage Examples

Health check:

```bash
curl -i http://localhost:8000/health
```

Valid stream request:

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u-1","session_id":"s-1","message":"hello"}'
```

Validation error example (empty/whitespace-only fields):

```bash
curl -i -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id":"   ","session_id":"s-1","message":""}'
```

Expected validation response shape:

```json
{
  "error_code": "ERR-VALIDATION-MISSING-FIELD",
  "message": "Validation failed for required fields.",
  "details": [
    { "field": "user_id", "issue": "Field required or empty after trim" }
  ]
}
```

## Tests

```bash
.\.venv\Scripts\python.exe -m pytest -q tests
```
