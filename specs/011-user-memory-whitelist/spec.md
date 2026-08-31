# Feature Specification: Long-Term User Memory Whitelist

**Feature Branch**: `[011-user-memory-whitelist]`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the eighth vertical slice: long-term, cross-session user memory storing a small whitelist of safe, non-sensitive facts, per US-009."

## Clarifications

### Session 2026-08-26

- Q: Which persistence format should this MVP use for long-term user memory: JSON file or SQLite file? → A: JSON file persistence on local disk.
- Q: Which office_region values are allowed for storage in this MVP? → A: Allow only APAC, EMEA, AMER.
- Q: If one message contains multiple candidate memory facts and only some are valid whitelist values, should the system save the valid ones and ignore the invalid ones, or reject the whole update? → A: Save valid fields, ignore invalid or non-whitelisted fields.
- Q: What timezone format should be persisted for the timezone field? → A: Store only common abbreviations (for example AEST, PST, CET).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture and Persist Whitelisted User Facts (Priority: P1)

As a returning user, I want the system to remember a small set of safe profile facts I explicitly state so I do not need to repeat them in every new conversation.

**Why this priority**: This is the core value of the slice: durable memory across sessions keyed by user identity.

**Independent Test**: Send a message that clearly states one whitelisted fact, then verify that fact is stored for the user_id and survives a service restart.

**Acceptance Scenarios**:

1. **Given** a message containing an explicit preferred device statement, **When** the message is processed, **Then** the preferred_device_type field is stored or updated for that user_id.
2. **Given** a message containing an explicit office region statement, **When** the message is processed, **Then** the office_region field is stored or updated for that user_id.
3. **Given** a message containing an explicit timezone statement, **When** the message is processed, **Then** the timezone field is stored or updated for that user_id.
4. **Given** stored whitelisted facts for a user_id, **When** the service restarts, **Then** those stored facts remain available.

---

### User Story 2 - Reuse Stored Facts Across Separate Sessions (Priority: P1)

As a returning user starting a new chat session, I want previously stored facts tied to my user_id to still be available so responses can remain context-aware without relying on session continuity.

**Why this priority**: Cross-session continuity is the explicit requirement distinguishing long-term memory from existing in-session behavior.

**Independent Test**: Store a fact in one request/session, send another request with a different session_id but same user_id, and verify the stored fact is accessible to the relevant response path.

**Acceptance Scenarios**:

1. **Given** a stored user memory profile and a new request with a different session_id but same user_id, **When** any intent path is executed, **Then** relevant stored facts are available to that path.
2. **Given** no stored facts for a user_id, **When** any intent path is executed, **Then** the response proceeds normally with no blocking behavior.
3. **Given** stored facts that are relevant to the current request, **When** a response is generated, **Then** those facts may be used naturally without requiring extra user prompts.

---

### User Story 3 - Enforce Strict Whitelist and Privacy Boundaries (Priority: P1)

As a security-conscious operator, I want only the approved safe fields persisted so the system never turns long-term memory into broad user tracking.

**Why this priority**: Safety and privacy constraints are mandatory for this slice and directly tied to acceptance requirements.

**Independent Test**: Submit messages containing non-whitelisted content and confirm no additional fields are persisted while normal responses continue.

**Acceptance Scenarios**:

1. **Given** a message containing content outside the three-field whitelist, **When** memory extraction runs, **Then** no non-whitelisted data is persisted.
2. **Given** a message containing PII or redacted placeholders, **When** memory extraction runs, **Then** those values are not persisted in long-term memory.
3. **Given** a request that does not contain extractable whitelist facts, **When** processing completes, **Then** no new memory fields are created and no response failure occurs.

---

### Edge Cases

- A single message contains multiple whitelisted facts; all detected whitelist fields are updated in one pass.
- A user later provides a new value for an existing whitelist field; the latest explicit user statement replaces the prior stored value.
- A message includes ambiguous location text that cannot be mapped to a coarse region; office_region is not updated.
- A message includes terms that resemble whitelist keywords but are not explicit user profile statements; no whitelist update is performed.
- A message contains office_region values outside APAC, EMEA, or AMER; unsupported values are ignored instead of stored.
- A message contains both valid whitelist facts and invalid or non-whitelisted candidates; valid whitelist facts are persisted while invalid candidates are ignored.
- A message includes timezone values not recognized as supported abbreviations; timezone is not updated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST persist long-term user memory keyed by user_id and independent of session_id.
- **FR-002**: System MUST support only this fixed whitelist of persisted fields: preferred_device_type, office_region, timezone.
- **FR-003**: System MUST NOT persist any field outside the fixed whitelist.
- **FR-004**: System MUST use JSON-file-backed local persistence suitable for MVP durability across process restarts.
- **FR-005**: System MUST detect explicit preferred_device_type statements from user messages using deterministic keyword/pattern matching.
- **FR-006**: System MUST detect explicit office_region statements from user messages using deterministic keyword/pattern matching and store only APAC, EMEA, or AMER values.
- **FR-007**: System MUST detect explicit timezone statements from user messages using deterministic keyword/pattern matching and persist only supported timezone abbreviations.
- **FR-008**: System MUST NOT use LLM-based extraction for this memory capture pass.
- **FR-009**: On detection, system MUST upsert each valid detected whitelist fact for the request user_id, and invalid or non-whitelisted candidates in the same message MUST be ignored.
- **FR-010**: System MUST make stored whitelist facts available to relevant intent-processing nodes for any request using that user_id.
- **FR-011**: Absence of stored facts MUST NOT block or degrade normal response flow for any intent.
- **FR-012**: System MUST NOT store message history, conversation summaries, or inferred preferences beyond explicit whitelist statements.
- **FR-013**: System MUST ignore and not persist PII values, redacted placeholders, and non-whitelisted content encountered in messages.
- **FR-014**: System MUST preserve existing stage 1-7 behavior outside the memory-specific additions.
- **FR-015**: System MUST keep out of scope for this pass: Arize Phoenix instrumentation, Promptfoo evaluation, and React frontend.

### Key Entities *(include if feature involves data)*

- **UserMemoryProfile**: Persistent per-user record keyed by user_id containing only preferred_device_type, office_region, and timezone.
- **MemoryExtractionResult**: Per-request extraction outcome listing which whitelist fields were detected, validated, and upserted.
- **MemoryStoreRecord**: Durable storage representation of UserMemoryProfile used for restart-safe persistence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid explicit whitelist fact statements are persisted to the correct user_id and retrievable in later requests.
- **SC-002**: 100% of requests using a new session_id with the same user_id can access previously stored whitelist facts.
- **SC-003**: 100% of non-whitelisted content and disallowed values are excluded from long-term persistence.
- **SC-004**: 100% of requests continue to complete normally regardless of whether stored facts exist.
- **SC-005**: Existing stage 1-7 contract/regression tests remain passing with no unintended behavior changes.

## Assumptions

- user_id is stable and trusted as the memory key across separate sessions.
- Whitelist extraction relies on deterministic phrase/pattern matching dictionaries consistent with current project conventions.
- office_region values are constrained to coarse region labels (for example APAC, EMEA, AMER) and not specific office addresses.
- When multiple explicit values for the same whitelist field are provided over time, the most recent explicit value is authoritative.
- A memory edit/delete management interface is out of scope for this MVP slice and may be introduced later.
