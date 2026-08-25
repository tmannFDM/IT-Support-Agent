# Data Model: RAG Policy Answers Slice

## Entity: PolicyDocument
- Purpose: Authoritative markdown policy source file used for retrieval indexing.
- Source set:
  - vpn_policy.md
  - password_policy.md
  - hardware_policy.md
  - software_policy.md
  - access_policy.md
- Required fields:
  - Header field: `Policy Category`
  - Body content: section/paragraph policy text
- Validation rules:
  - Files are ingested as-is; no content rewriting.
  - Missing `Policy Category` is ingestion-invalid for metadata completeness.

## Entity: PolicyChunk
- Purpose: Coherent retrievable unit derived from PolicyDocument section or paragraph.
- Fields:
  - chunk_id: str
  - text: str
  - policy_category: str
  - source_document: str
- Validation rules:
  - `text` must be non-empty.
  - `policy_category` must map from source file header.
  - `source_document` must equal originating filename.

## Entity: RetrievalResultItem
- Purpose: One ranked retrieval hit for a policy query.
- Fields:
  - chunk_id: str
  - text: str
  - score: float
  - policy_category: str
  - source_document: str
- Validation rules:
  - score is numeric and comparable against threshold.

## Entity: RetrievalResultSet
- Purpose: Query-time context selection bundle.
- Fields:
  - query: str
  - items: list[RetrievalResultItem]
  - threshold: float (fixed at 0.35)
  - above_threshold_items: list[RetrievalResultItem]
- Validation rules:
  - maximum top-k retrieved items considered for generation: 3.
  - only items with score >= 0.35 are usable context.

## Entity: PolicyAnswerState (AgentState extension)
- Purpose: Node-level state for policy question answering.
- Fields:
  - question: str
  - retrieved_chunks: list[RetrievalResultItem]
  - used_context: bool
  - response: str
  - error: str
  - cited_sources: list[str]
- State transitions:
  - Context available:
    - retrieve top-3 -> filter by threshold -> call LLM -> append source citations -> set response
  - No context available:
    - skip LLM -> set fixed response `I don't have information on that policy.`
  - LLM failure:
    - set error (stream emits `intent` then `error`, no `done`)

## Entity: ChatStreamEvent (existing envelope)
- Purpose: Streaming transport contract for `/chat/stream`.
- Fields:
  - event_type: Literal[token, tool_call, error, done, intent]
  - data: str
- Policy-question path transitions:
  - success: `intent` -> `token`(answer with source filenames) -> `done`
  - no-context fallback: `intent` -> `token`(fixed fallback) -> `done`
  - generation error: `intent` -> `error` -> terminate (no `done`)

## Regression Contract Entities (unchanged)
- ValidationErrorResponse:
  - HTTP 422 with existing error_code and details shape.
- DisconnectTermination:
  - Immediate stop, no retry, no post-disconnect events.
- TicketStatusFlow:
  - Existing stage-3 action_request ticket-status behavior unchanged.
- DirectResponseFlow:
  - Existing stage-2 direct_response behavior unchanged.
