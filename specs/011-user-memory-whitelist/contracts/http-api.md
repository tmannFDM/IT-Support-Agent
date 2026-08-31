# HTTP Contract: Long-Term User Memory Whitelist

## Endpoint: POST /chat/stream

### Request body
- Existing request schema remains unchanged.

### Stream envelope
- Existing SSE envelope remains unchanged:

```json
{
  "event_type": "intent | token | tool_call | error | done",
  "data": "string"
}
```

## Memory-capture behavior contract
For every request with a valid user_id:
1. Guardrail redaction runs first.
2. Deterministic memory extraction checks redacted message for whitelist facts.
3. Valid detected facts are upserted by user_id in JSON-backed storage.
4. Invalid/non-whitelisted candidates are ignored.
5. Request flow continues to intent classification and response generation.

## Whitelist persistence contract
- Persisted fields are strictly limited to:
  - preferred_device_type in {`laptop`, `desktop`}
  - office_region in {`APAC`, `EMEA`, `AMER`}
  - timezone in {`AEST`, `PST`, `EST`, `CET`, `GMT`}
- No message history, summaries, raw PII, or other inferred/profile fields may be stored.
- Persistence survives server restart via on-disk JSON file.

## Cross-session retrieval contract
- Memory lookup key is user_id, not session_id.
- A request with a new session_id and same user_id can read previously stored facts.
- Absence of stored facts must not change event ordering or block responses.

## Optional context-use contract
- At minimum `answer_policy_question_node` and `generate_response_node` may receive stored facts in node context.
- Nodes may use facts naturally when relevant but must not fabricate missing facts.
- Nodes must not require facts as a precondition for producing responses.

## Acceptance-oriented contract scenarios
1. Fact persistence and retrieval across separate requests with same user_id and different session_id.
2. Mixed candidate input where one valid and one non-whitelisted candidate appear: only valid fact persists.
3. Simulated restart re-loads JSON file and retains stored facts.
4. Request with no memory-relevant content behaves equivalently whether facts exist or not.

## Unchanged contracts
- Ticket creation/status behavior remains unchanged.
- Password reset behavior remains unchanged.
- RAG retrieval/generation behavior remains unchanged.
- Prompt-injection blocking and PII redaction semantics remain unchanged beyond memory wiring.
