# Runtime Contract: Shared Local LLM Configuration

## Scope
This contract defines runtime configuration behavior for conversational generation paths only.

## Shared Configuration Contract
- The system exposes one shared API URL configuration for LLM chat calls.
- The system exposes one shared model configuration for LLM chat calls.
- Both `direct_response` and `policy_question` paths must resolve endpoint and model from the same shared configuration source.

## Provider Alignment Contract
- Active conversational behavior must not depend on external-provider API key presence.
- OpenAI-specific default constants are not part of active runtime behavior for this feature pass.

## Behavioral Contract (unchanged)
- Direct response success stream sequence remains: `intent`, `token`, `done`.
- Policy question success stream sequence remains: `intent`, `token`, `done`.
- Generation failure stream sequence remains: `intent`, `error`, no `done`.

## Out of Scope
- No schema updates.
- No API route changes.
- No RAG module changes.
- No ticket-tool behavior changes.
