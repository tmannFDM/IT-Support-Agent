# Feature Specification: In-Session Conversation History Window

**Feature Branch**: `[012-session-history-window]`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Extend the IT Support Ticketing System with the ninth vertical slice: short-term, in-session conversation history using a bounded sliding window, per US-008 and NFR-006."

## Clarifications

### Session 2026-08-31

- Q: Which form of prior turns should be kept in the session history window for later prompt context? → A: Store redacted user/assistant text only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contextual Follow-Up Answers (Priority: P1)

As an employee asking policy or direct support questions, I can ask a follow-up question in the same conversation without repeating full context, and the assistant still responds based on earlier turns.

**Why this priority**: Follow-up understanding is the core user value of this slice and directly improves answer quality for common multi-turn support conversations.

**Independent Test**: Can be fully tested by asking an initial policy or direct support question and then a follow-up in the same session; value is delivered if the second response correctly uses prior context.

**Acceptance Scenarios**:

1. **Given** a session where the user asked a VPN policy question and received a response, **When** the same user asks "what about for contractors?" in the same session, **Then** the assistant interprets the follow-up using the earlier VPN context and returns a relevant answer.
2. **Given** a session where the user asked a direct support question and got a completed response, **When** they ask a related follow-up in that same session, **Then** the assistant uses recent session turns to answer the follow-up without requiring the user to restate the original topic.

---

### User Story 2 - Session-Isolated Short-Term Memory (Priority: P1)

As a user, I can trust that my short-term conversation context is isolated to my current session and never mixed with another session, even when the same account is used.

**Why this priority**: Session isolation is a privacy and correctness requirement; cross-session leakage would create both security risk and incorrect behavior.

**Independent Test**: Can be fully tested by creating two sessions under the same user, adding history in one, and confirming the other session starts with no short-term history.

**Acceptance Scenarios**:

1. **Given** session A has prior turns and session B is newly created for the same user, **When** a follow-up-style question is asked in session B, **Then** no context from session A is available to influence the response.
2. **Given** two different active session IDs, **When** conversation turns are stored after completed responses, **Then** each session only receives its own turns.

---

### User Story 3 - Bounded History and Stable Existing Behavior (Priority: P2)

As a system owner, I need short-term history to remain bounded and non-disruptive so conversation context is useful without unbounded growth or regressions in existing tool paths.

**Why this priority**: Bounded history protects response cost and latency targets, while preserving existing behavior avoids regression in previously delivered slices.

**Independent Test**: Can be fully tested by adding turns beyond the configured limit and confirming oldest-turn eviction, while re-running existing tool-oriented scenarios to confirm no behavior change.

**Acceptance Scenarios**:

1. **Given** a per-session history limit of 5 completed exchanges, **When** a 6th completed exchange is added, **Then** the oldest exchange is removed and the 5 most recent exchanges remain.
2. **Given** a ticket status, password reset, or ticket creation request, **When** the request is processed, **Then** routing and extraction behavior remains based on the current message only and is unchanged by short-term history.
3. **Given** a response stream that has not reached completion, **When** processing is still in progress, **Then** the in-progress turn is not added to short-term history until response completion.

### Edge Cases

- A new or unknown session ID starts with empty short-term history.
- If a response fails or is interrupted before completion, the turn is not appended as a completed exchange.
- If the user sends repeated follow-up questions rapidly in one session, ordering is preserved and eviction still removes only the oldest completed exchange when the limit is exceeded.
- Long-term user memory facts may still be available per existing behavior, but they must not be used as a substitute for session history isolation rules.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain short-term conversation history keyed by session ID.
- **FR-002**: System MUST treat short-term conversation history as ephemeral session-scoped data that is independent from long-term per-user memory.
- **FR-003**: System MUST store each history entry as a completed exchange containing the triggering user message and the corresponding assistant response, with both texts stored in redacted form.
- **FR-004**: System MUST append a completed exchange only after the assistant response is complete.
- **FR-005**: System MUST enforce a fixed maximum number of recent exchanges per session.
- **FR-006**: System MUST evict the oldest exchange when adding a new exchange would exceed the configured per-session maximum.
- **FR-007**: System MUST include recent session history as prior conversation context for direct support responses and policy-question responses, using only the stored redacted exchange texts.
- **FR-008**: System MUST keep ticket status, password reset, and ticket creation routing/extraction behavior history-independent for this slice.
- **FR-009**: System MUST ensure short-term history from one session ID is never available to any other session ID, including sessions belonging to the same user.
- **FR-010**: System MUST preserve behavior from slices 1-8 outside the explicitly added short-term context behavior.
- **FR-011**: System MUST require no new client-facing endpoint for short-term history in this slice.

### Key Entities *(include if feature involves data)*

- **Session History Store**: Session-scoped collection of recent completed exchanges indexed by session ID.
- **Completed Exchange**: A paired record of one user message and one assistant response captured after response completion, with both message texts stored as redacted content.
- **History Window Policy**: Rule set defining the maximum retained exchanges and oldest-first eviction behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, at least 95% of same-session follow-up questions that rely on the immediately prior topic are answered with contextually relevant continuity.
- **SC-002**: In isolation tests, 100% of new sessions start with empty short-term history and show no cross-session context leakage.
- **SC-003**: In bounded-window tests, 100% of over-limit insertions evict exactly one oldest exchange and retain exactly the most recent configured number of exchanges.
- **SC-004**: Existing regression suite coverage for prior slices remains at current pass rate, including tool-invoking paths that continue to operate from current-message input only.

## Assumptions

- The per-session history limit for this slice is fixed and configured to 5 exchanges unless changed by product direction in a later slice.
- A completed exchange is defined by completion of the assistant response event and excludes partial or failed responses.
- Session history retains redacted text only and does not retain raw unredacted turn content.
- Existing long-term per-user memory behavior remains unchanged and coexists with session-scoped short-term history.
- Frontend display and management of short-term conversation history are addressed in a later frontend-focused slice.

## Out of Scope

- Any React frontend changes for displaying history.
- Any Arize Phoenix instrumentation work.
- Any Promptfoo evaluation integration.
- Any new API endpoint for fetching short-term session history in this slice.
