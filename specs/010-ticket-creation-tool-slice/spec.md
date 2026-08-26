# Feature Specification: Ticket Creation Tool Slice

**Feature Branch**: `[010-ticket-creation-tool-slice]`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the seventh vertical slice: a FastMCP ticket creation tool, replacing the placeholder response for ticket-creation action_requests."

## Clarifications

### Session 2026-08-26

- Q: When a ticket description matches keywords from multiple categories, which rule should choose the final category? → A: Use a fixed precedence order: Access > VPN > Password > Hardware > Software.
- Q: How should the system handle ticket_id generation when the next computed TKT-#### value already exists in the in-memory store? → A: Increment until an unused TKT-#### is found.
- Q: If no priority keywords are detected but category is clear, what default priority should be assigned? → A: medium.
- Q: If a user message contains both ticket-creation and ticket-status cues, which route should take precedence? → A: Prioritize ticket-status lookup when a valid ticket ID is present.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create IT Ticket from Action Request (Priority: P1)

As an employee reporting an issue, I want to create a support ticket from chat so I receive a new ticket ID and confirmation without manual handoff.

**Why this priority**: This is the core value of the seventh vertical slice and replaces the current placeholder behavior for ticket-creation requests.

**Independent Test**: Submit a clear, categorizable ticket-creation request and verify stream events are intent, tool_call with full TicketCreateResponse, token confirmation containing new ticket ID, then done.

**Acceptance Scenarios**:

1. **Given** a ticket-creation-specific action request with a clear issue description, **When** the request is processed, **Then** routing reaches create_ticket_node instead of generic action placeholder and ticket-status lookup path.
2. **Given** a categorizable request, **When** category and priority are inferred from established keyword conventions, **Then** create_ticket tool is executed and emits a tool_call payload with category, priority, generated ticket_id, and status `open`.
3. **Given** a successful ticket creation, **When** stream events are emitted, **Then** a human-readable token confirmation includes the newly generated ticket_id and is followed by done.

---

### User Story 2 - Fail Safe for Uncategorizable Requests (Priority: P1)

As a support operator, I want uncategorizable requests rejected with a clear error so the system avoids creating incorrectly classified tickets.

**Why this priority**: Avoiding miscategorized tickets is safer than guessing and aligns with existing fail-safe behavior in prior stages.

**Independent Test**: Submit a vague description with no category keyword match and verify an error event is returned rather than creating a ticket.

**Acceptance Scenarios**:

1. **Given** a ticket-creation request with no detectable category keyword match, **When** create_ticket_node evaluates the message, **Then** no ticket is created and an error event asks for more detail.
2. **Given** an uncategorizable request, **When** stream output is generated, **Then** the response uses error semantics instead of guessed tool_call output.

---

### User Story 3 - New Ticket Immediately Lookupable (Priority: P2)

As an employee or agent, I want newly created tickets to be immediately retrievable by ID so I can verify ticket status right away.

**Why this priority**: Immediate lookup confirms state consistency between ticket creation and existing ticket-status capabilities.

**Independent Test**: Create a ticket, capture returned ticket_id, then issue a status lookup request and verify the existing ticket_status_lookup tool returns that new ticket.

**Acceptance Scenarios**:

1. **Given** a newly created ticket ID from create_ticket response, **When** ticket_status_lookup is called with that ID, **Then** the ticket is found in the same in-memory mocked store.
2. **Given** stage 1-6 existing workflows, **When** regression tests run, **Then** prior behavior remains unchanged outside this new ticket-creation slice.

---

### Edge Cases

- A request contains mixed signals across multiple categories; system resolves category deterministically with precedence Access > VPN > Password > Hardware > Software.
- A request indicates high severity language (for example service down/cannot work) while category is clear; priority inference escalates appropriately without changing category logic.
- A request has a clear category but no priority keywords; system assigns default priority `medium`.
- A request contains both ticket-creation language and a valid ticket ID; system prioritizes ticket-status lookup path over ticket-creation path.
- A request is clearly a ticket-creation intent but description lacks category indicators; system returns an error asking for more detail rather than guessing.
- Newly generated ticket IDs always follow TKT-#### format, and on collision the system increments until an unused ID is found.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a FastMCP tool named `create_ticket` that accepts category, priority, and description inputs.
- **FR-002**: System MUST validate ticket creation inputs with `TicketCreateRequest` using category literals `VPN`, `Password`, `Hardware`, `Software`, `Access` and priority literals `low`, `medium`, `high`, `critical`.
- **FR-003**: System MUST return ticket creation output with `TicketCreateResponse` including category, priority, description, generated `ticket_id`, and status `open`.
- **FR-004**: System MUST generate new ticket IDs in `TKT-####` format, consistent with the mocked ticket store convention, and on collision MUST increment until an unused ID is found.
- **FR-005**: System MUST route ticket-creation-specific action requests (including intent phrases such as create/open/log/file ticket/request) to a dedicated create_ticket_node distinct from ticket-status and password-reset paths, except when a valid ticket ID is present, in which case ticket-status lookup MUST take precedence.
- **FR-006**: System MUST infer category from free-text description using established keyword-based category mapping patterns already used in the project and MUST resolve multi-category matches using precedence Access > VPN > Password > Hardware > Software.
- **FR-007**: System MUST infer priority from severity language using established keyword-based inference patterns, MUST default to `medium` when no priority keywords are detected and category is clear, and MUST NOT use LLM-based classification in this slice.
- **FR-008**: System MUST return an error event requesting more issue detail when no category keyword match is found.
- **FR-009**: System MUST NOT create a ticket when category cannot be determined.
- **FR-010**: On successful creation, system MUST add the new ticket to the same mocked in-memory store used by ticket_status_lookup.
- **FR-011**: On successful creation, stream output MUST follow intent -> tool_call (full TicketCreateResponse JSON) -> token confirmation including ticket_id -> done.
- **FR-012**: System MUST allow the newly created ticket_id to be looked up immediately through existing ticket_status_lookup behavior.
- **FR-013**: System MUST preserve existing stage 1-6 behavior outside ticket-creation-specific routing and processing.
- **FR-014**: System MUST keep out of scope: long-term memory, Arize Phoenix instrumentation, Promptfoo evaluation, and React frontend.

### Key Entities *(include if feature involves data)*

- **TicketCreateRequest**: Input entity for ticket creation containing category, priority, and issue description under existing category/priority conventions.
- **TicketCreateResponse**: Output entity containing category, priority, description, generated ticket_id, and status `open`.
- **TicketCreationInferenceResult**: Internal routing and inference entity capturing detected creation intent, inferred category, inferred priority, and validation state.
- **MockTicketStoreEntry**: In-memory ticket record entity shared between ticket creation and ticket_status_lookup for immediate consistency.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of clear, categorizable ticket-creation requests produce tool_call payloads with valid TicketCreateResponse and new ticket_id in TKT-#### format.
- **SC-002**: 100% of uncategorizable ticket-creation requests return an error event and create no ticket.
- **SC-003**: 100% of newly created ticket IDs can be looked up immediately via existing ticket_status_lookup behavior.
- **SC-004**: Existing stage 1-6 contract/regression tests remain passing with no unintended behavior changes.

## Assumptions

- Existing category and priority literal conventions are already authoritative in the codebase and reused without expansion.
- The mocked in-memory ticket store is the canonical state source for ticket_status_lookup and will accept new entries in this slice.
- Keyword-based intent/category/priority inference patterns are already established and should be extended consistently rather than replaced.
- Error-response semantics for uncategorizable input follow existing stream error behavior patterns used in prior slices.
