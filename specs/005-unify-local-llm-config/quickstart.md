# Quickstart: Validate Shared Local LLM Configuration Correction

## Prerequisites
- Python 3.11+
- Existing service setup from prior slices
- Local Ollama runtime available
- Model configured and available locally

## Scope for this pass
Only change:
- `src/agent/prompts.py`
- `src/agent/nodes.py`

Do not change:
- schemas
- route wiring
- RAG modules
- ticket tool
- stream event contract

## Run tests

```bash
./.venv/Scripts/python.exe -m pytest -q tests
```

## Validation Scenario A: direct response path
- Send a direct conversational message.
- Confirm response stream remains `intent` -> `token`(s) -> `done`.
- Confirm no external-provider credential dependency is required for active path behavior.

## Validation Scenario B: policy question path
- Send a policy question covered by existing policy docs.
- Confirm policy stream remains `intent` -> `token` -> `done`.
- Confirm endpoint/model resolution uses shared local configuration source.

## Validation Scenario C: generation failure behavior
- Simulate a generation failure in either path.
- Confirm stream remains `intent` -> `error` and terminates without `done`.

## Regression expectation
- Existing stage-1/2/3/4 tests pass unchanged with no new acceptance criteria.

## Verification Notes
- Contract test run: `./.venv/Scripts/python.exe -m pytest -q tests/contract/test_chat_stream.py` -> `14 passed, 2 warnings`.
- Full suite run: `./.venv/Scripts/python.exe -m pytest -q tests` -> `15 passed, 2 warnings`.
- Implementation scope remained limited to `src/agent/prompts.py` and `src/agent/nodes.py`.
