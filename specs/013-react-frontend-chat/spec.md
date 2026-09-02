# Feature Specification: React Frontend Chat Experience

**Feature Branch**: `[013-react-frontend-chat]`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Build the React frontend for the IT Support Ticketing System, per NFR-002 and US-007/US-008 acceptance criteria, consuming existing /chat/stream and /health behavior with no backend changes."

## Clarifications

### Session 2026-08-31

- Q: How should the frontend behave if the health check fails at page load or just before sending a message? → A: Skip health gating and handle failures from chat stream responses.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Streamed Chat Interaction (Priority: P1)

As an IT support user, I can send a message and immediately see my message in the conversation while the assistant response streams in live so the interface feels responsive and readable.

**Why this priority**: End-to-end chat usability is the core value of this frontend slice and is required for validating the existing backend workflow through the browser.

**Independent Test**: Can be fully tested by opening the page, sending a valid message, and observing immediate user bubble rendering followed by incremental assistant token rendering and completion handling.

**Acceptance Scenarios**:

1. **Given** the chat page is loaded, **When** the user submits a non-empty message, **Then** the user message appears immediately in the conversation list before the assistant response completes.
2. **Given** a response stream is active, **When** token events arrive, **Then** the current assistant message bubble updates progressively as new text is received.
3. **Given** a response stream is active, **When** a done event arrives, **Then** loading state ends and message input becomes available for the next user message.

---

### User Story 2 - Structured Action Results and Safe Error Display (Priority: P1)

As an IT support user, I can understand tool-based outcomes and blocked/error outcomes through clean UI elements rather than raw backend payloads.

**Why this priority**: Tool outputs and safety errors are central to US-007 behavior and must be understandable without exposing internal payload formatting or stack traces.

**Independent Test**: Can be fully tested by triggering tool responses and blocked/error responses, then verifying card rendering for tool data and sanitized error messaging.

**Acceptance Scenarios**:

1. **Given** a tool_call event for ticket status, password reset, or ticket creation, **When** the payload is received, **Then** the UI renders a typed, structured card variant for that tool result instead of raw JSON.
2. **Given** an intent event is received, **When** the event is processed, **Then** intent is logged for debugging and not shown as a user-facing chat bubble.
3. **Given** an error event is received, **When** the payload is parsed, **Then** the UI shows only a user-safe message field in a distinct error style and does not display raw JSON or stack text.

---

### User Story 3 - Session-Scoped Frontend Continuity (Priority: P2)

As an IT support user, I can continue a conversation within one open page session using stable user/session identifiers, while understanding that only current-page conversation history is displayed.

**Why this priority**: This provides US-008 frontend continuity without requiring new backend endpoints or cross-session browsing in this pass.

**Independent Test**: Can be fully tested by loading the page, confirming generated identifiers are reused for multiple requests in that page session, and verifying conversation history remains visible in-order in the scrolling view.

**Acceptance Scenarios**:

1. **Given** the page loads for a new browser session, **When** identifiers are initialized, **Then** one user identifier and one session identifier are generated and used in all request payloads for that page session.
2. **Given** multiple messages are exchanged in one page session, **When** conversation is rendered, **Then** user and assistant messages remain visible in chronological order in the same conversation view.
3. **Given** the user attempts to submit an empty or whitespace-only message, **When** client-side validation runs, **Then** submission is blocked gracefully and the interface remains stable.

### Edge Cases

- Response stream includes an error event before any token event.
- Tool_call payload cannot be mapped to a known card variant; UI falls back to a safe unknown-result representation without exposing raw payload text.
- Network interruption during stream parsing leaves the UI in a recoverable state and allows a new request.
- Health endpoint failure does not block sending; request failure handling remains driven by chat stream errors.
- Backend returns validation failure despite client-side checks; UI shows a safe error message and remains usable.
- Policy response includes source citation text in the streamed answer; citation text is preserved in displayed assistant content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single-page chat interface with message input, send control, and scrolling conversation display.
- **FR-002**: System MUST consume existing chat streaming behavior using POST requests with JSON body fields for user identifier, session identifier, and message.
- **FR-003**: System MUST process streamed server-sent data by parsing `data:` lines from the response stream.
- **FR-004**: System MUST append user messages to the conversation immediately upon valid submit.
- **FR-005**: System MUST stream assistant token content into the active assistant message bubble as token events arrive.
- **FR-006**: System MUST end loading state and re-enable input only when done event processing completes.
- **FR-007**: System MUST render tool_call results as structured typed cards for ticket status, password reset, and ticket creation outputs.
- **FR-008**: System MUST style each tool result card variant distinctly enough to be visually differentiable.
- **FR-009**: System MUST not display intent events in chat output and MUST log them for debugging visibility.
- **FR-010**: System MUST render error events as visually distinct safe error messages using the parsed message field only.
- **FR-011**: System MUST never render raw error JSON payloads or stack traces to end users.
- **FR-012**: System MUST generate user and session identifiers at page load and reuse them for every request in that page session.
- **FR-013**: System MUST prevent empty or whitespace-only message submission client-side and remain stable if backend validation errors still occur.
- **FR-014**: System MUST preserve policy answer citation text as part of displayed assistant responses when present.
- **FR-015**: System MUST treat health endpoint checks as optional informational signals and MUST NOT block chat submission based on health-check failure.
- **FR-016**: System MUST not require new backend endpoints, backend schema changes, or backend behavior changes for this slice.

### Key Entities *(include if feature involves data)*

- **Conversation Message**: One rendered chat item with role (user, assistant, error), content, ordering, and streaming/completed state.
- **Stream Event**: One parsed event containing event type and data payload used to drive UI updates.
- **Tool Result Card**: Structured presentation model for one of three action result types (ticket status, password reset, ticket creation).
- **Client Session Identity**: Pair of generated identifiers (user identifier and session identifier) scoped to a loaded page session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In manual walkthrough testing, 100% of valid user submissions display the user message immediately and then show streamed assistant progression until completion.
- **SC-002**: In tool-flow validation scenarios, 100% of tool_call responses are shown as structured card variants and 0% are rendered as raw JSON text.
- **SC-003**: In blocked/error scenarios, 100% of visible error outputs show a clear safe message and 0% expose stack traces or unformatted backend payloads.
- **SC-004**: In policy-question scenarios with citations, citation text appears in the final rendered assistant message in at least 95% of sampled runs.
- **SC-005**: The interface supports a complete manual walkthrough covering all existing backend stage behaviors without requiring backend modifications.

## Assumptions

- Existing backend `/chat/stream` and `/health` contracts remain stable for this frontend slice.
- Current-session conversation rendering on the page satisfies frontend history visibility needs for this pass.
- Authentication and cross-session user identity management are out of scope and deferred.
- The frontend stack requirement in NFR-002 is enforced in implementation planning and execution for this feature.

## Out of Scope

- Backend logic changes for memory, tool logic, retrieval, or safety checks.
- Cross-session conversation browsing or historical ticket browsing UI.
- User-facing display of long-term memory facts.
- Authentication/login flows.
- Arize Phoenix or Promptfoo integration.
- Visual polish beyond baseline readability and simple distinct tool-card styling.
