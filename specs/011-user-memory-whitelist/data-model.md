# Data Model: Long-Term User Memory Whitelist

## Entity: UserMemoryFacts
- Purpose: Closed whitelist facts persisted per user_id across sessions.
- Fields:
  - preferred_device_type: Literal[`laptop`, `desktop`] | None
  - office_region: Literal[`APAC`, `EMEA`, `AMER`] | None
  - timezone: Literal[`AEST`, `PST`, `EST`, `CET`, `GMT`] | None
- Validation rules:
  - Only the three whitelist fields are permitted.
  - Missing fields remain unset and do not block response paths.
  - Invalid/non-whitelisted candidate values are ignored per-field.

## Entity: UserMemoryRecord
- Purpose: Durable JSON record for one user.
- Fields:
  - user_id: str
  - facts: UserMemoryFacts
  - updated_at: str (optional metadata for record freshness)
- Validation rules:
  - user_id is the sole key used for cross-session retrieval.
  - No message history, summaries, or inferred fields are stored.

## Entity: UserMemoryStoreFile
- Purpose: On-disk JSON persistence container surviving restart.
- Fields:
  - records: mapping of user_id -> UserMemoryRecord or equivalent normalized JSON structure
- Validation rules:
  - File reads and writes must preserve existing user records.
  - Writes apply partial upserts for valid detected fields only.

## Entity: MemoryExtractionResult
- Purpose: Per-request extraction outcome used by agent flow.
- Fields:
  - detected_preferred_device_type: Literal[`laptop`, `desktop`] | None
  - detected_office_region: Literal[`APAC`, `EMEA`, `AMER`] | None
  - detected_timezone: Literal[`AEST`, `PST`, `EST`, `CET`, `GMT`] | None
  - ignored_candidates: list[str]
- Validation rules:
  - Extraction uses deterministic keyword/pattern matching only.
  - PII/redacted placeholders and non-whitelisted candidates are ignored.

## Agent State Additions
- Optional `user_memory_facts` object attached to state after guardrail step for downstream node use.
- Optional fact fragments may be attached only when valid values are detected.

## State Transitions
1. Request enters guardrail flow and redaction executes.
2. Memory extraction runs on redacted message and upserts valid fields by user_id.
3. Stored facts for user_id are loaded into state for downstream nodes.
4. Intent classification and node execution proceed regardless of whether facts exist.
5. Relevant response nodes may optionally incorporate available facts in context.
