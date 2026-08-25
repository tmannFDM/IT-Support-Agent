# Data Model: Unify Local LLM Configuration

## Entity: SharedLLMConfiguration
- Purpose: Single runtime configuration used by all conversational generation paths.
- Fields:
  - llm_api_url: str
  - llm_model: str
- Validation rules:
  - `llm_api_url` must point to reachable local Ollama chat endpoint when defaults are used.
  - `llm_model` must identify an available local model.

## Entity: GenerationPath
- Purpose: Existing conversational generation flows that consume `SharedLLMConfiguration`.
- Values:
  - direct_response
  - policy_question
- Validation rules:
  - Both paths must read from the same configuration source.
  - Neither path should require external-provider API key configuration.

## Entity: StreamContractOutcome (unchanged)
- Purpose: Existing SSE sequence outcomes that must remain stable.
- Success sequence:
  - intent -> token(s) -> done
- Error sequence:
  - intent -> error and terminate (no done)
- Validation rules:
  - No new event types are introduced by this correction.
  - Existing stage-1/2/3/4 test expectations remain unchanged.
