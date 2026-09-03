# Feature Specification: Frontend Polish – Demo Features

**Feature Branch**: `[014-frontend-polish]`

**Created**: 2026-09-02

**Status**: Draft

**Input**: Extend the React frontend with four independent demo-polish features: new session button, persona switcher, visible intent badges, and quick-prompt buttons. No backend changes required.

## Clarifications

### Session 2026-09-02

- Q: What are the exact fixed UUID values for each persona, and where should they be stored? → A: Store three personas in `frontend/src/constants.ts`: Alex (`550e8400-e29b-41d4-a716-446655440001`), Jordan (`550e8400-e29b-41d4-a716-446655440002`), Sam (`550e8400-e29b-41d4-a716-446655440003`).
- Q: What are the exact 4-5 quick-prompt messages you want pre-configured in the buttons? → A: Five exact prompts verified this session: (1) "Check ticket TKT-1001" (ticket lookup), (2) "What's the VPN policy?" (RAG with citation), (3) "My VPN keeps disconnecting, please create a ticket" (ticket creation success path), (4) "Reset my password, I'm locked out, employee EMP-9" (malformed ID, escalation demo), (5) "ignore previous instructions" (injection prevention).
- Q: When the backend doesn't send an `intent` event, should the intent badge be hidden entirely or show a fallback "Unknown" badge? → A: Hide badge completely—no badge renders if no intent event received (Option A).
- Q: What color scheme should the intent badge use? → A: Intent-specific colors with TailwindCSS: `policy_question` → blue (`bg-blue-100 text-blue-700`), `action_request` → amber (`bg-amber-100 text-amber-700`), `direct_response` → gray (`bg-gray-200 text-gray-700`), `escalation` → orange (`bg-orange-100 text-orange-700`), `blocked` → red (`bg-red-100 text-red-700`).
- Q: Which persona should be pre-selected on first load? → A: Alex (Option A, natural default as first in array).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New Session Button (Priority: P1)

Users want to start a fresh conversation without reloading the page. A prominent "New chat" button in the header clears the visible message list, generates a fresh `session_id` via `crypto.randomUUID()`, and preserves the existing `user_id` unchanged. This allows users to maintain their identity while starting a clean conversation thread.

**Why this priority**: Essential for usability—users frequently need to start over mid-conversation without losing their authenticated identity. Demonstrates session management capability.

**Independent Test**: Click "New chat" button → verify message list is cleared → verify a new message sent includes a different `session_id` (logged to console) → verify `user_id` is unchanged.

**Acceptance Scenarios**:

1. **Given** the chat has existing messages, **When** user clicks "New chat", **Then** the message list clears and the UI is ready for input.
2. **Given** "New chat" was clicked, **When** user sends a message, **Then** a new `session_id` is generated and used in the request.
3. **Given** "New chat" was clicked, **When** user sends a message, **Then** the `user_id` remains the same as before the click.

---

### User Story 2 - Persona Switcher (Priority: P1)

Users want to switch between multiple named personas (e.g., "Alex", "Jordan", "Sam"), each with a stable, fixed UUID. Switching personas mid-session clears messages and generates a fresh `session_id`, treating it like a new conversation (because switching "who you are" implies a new context). The last-selected persona persists in localStorage so page refreshes maintain the same persona.

**Why this priority**: Critical for multi-user demo scenarios and showcasing the backend's ability to differentiate users. Persona switching is a distinct user journey that must work independently.

**Independent Test**: Switch to persona "Jordan" → send a message and verify `user_id` matches Jordan's UUID → switch to persona "Sam" → verify messages are cleared, new `session_id` generated, and `user_id` now matches Sam's UUID → reload page and verify "Sam" is still selected.

**Acceptance Scenarios**:

1. **Given** the default persona is selected, **When** user clicks the persona dropdown, **Then** a list of 2-3 personas is shown (e.g., "Alex", "Jordan", "Sam").
2. **Given** persona "Jordan" is selected, **When** user sends a message, **Then** the request includes Jordan's fixed UUID and a `session_id`.
3. **Given** user has sent messages, **When** they switch to persona "Sam", **Then** the message list clears and a fresh `session_id` is generated.
4. **Given** user switches to persona "Sam" and sends a message, **When** they reload the page, **Then** persona "Sam" is pre-selected and localStorage reflects the choice.
5. **Given** user switches back to persona "Jordan", **When** they send a message, **Then** Jordan's UUID is used (same as before, not regenerated).

---

### User Story 3 - Visible Intent Badges (Priority: P2)

Users want to see which intent/action category the backend detected for their query. A small, subtly-styled badge (e.g., a pill with the intent name) appears beneath each assistant message, sourced from the `intent` event. Backend console logging continues for debugging; the badge is added alongside existing logging.

**Why this priority**: Improves transparency and helps users understand how their intent is being interpreted. Useful for demonstrating the intent classification pipeline without disrupting core chat flow.

**Independent Test**: Send a message that triggers an intent event → verify intent badge appears beneath the assistant response → verify browser console also logs the intent for debugging.

**Acceptance Scenarios**:

1. **Given** a message triggers an intent event (e.g., "ticket_lookup"), **When** the response streams, **Then** an intent badge appears beneath the assistant message showing the intent name.
2. **Given** an intent badge is visible, **When** browser console is opened, **Then** the intent is also logged for debugging (existing behavior preserved).
3. **Given** multiple messages are sent, **When** each response arrives, **Then** each assistant message has the correct intent badge.
4. **Given** a message does not trigger an intent event, **When** the response arrives, **Then** no badge is displayed (or a default "unknown" badge appears).

---

### User Story 4 - Quick-Prompt Buttons (Priority: P2)

Users want instant access to example queries demonstrating major capabilities. A row of 4-5 pre-written quick-prompt buttons appears above the input field (e.g., "Check ticket TKT-1001", "What's the VPN policy?", "Reset my password", "ignore previous instructions"). Clicking a button populates the input field and sends it immediately, following the same flow as manual typing.

**Why this priority**: Lowers barrier to entry for first-time users and demonstrates feature breadth. Enables easy demo walkthroughs showing different backend capabilities.

**Independent Test**: Click "Check ticket TKT-1001" → verify input field is populated → verify message is sent immediately → verify response flows normally.

**Acceptance Scenarios**:

1. **Given** the chat interface is loaded, **When** user looks at the input area, **Then** a row of 4-5 quick-prompt buttons is visible.
2. **Given** the quick-prompt button "Check ticket TKT-1001" is visible, **When** user clicks it, **Then** the input field is populated with that text.
3. **Given** input is populated by a quick-prompt, **When** the send flow executes, **Then** the message is sent immediately without requiring manual send action.
4. **Given** a quick-prompt message is sent, **When** the response arrives, **Then** it flows through the normal stream, intent, tool, and error paths.
5. **Given** user manually types while a quick-prompt is in the input, **When** they click a different quick-prompt, **Then** the manual text is replaced and the new prompt is sent.

---

### Edge Cases

- What happens if user switches personas while a message is streaming? (Answer: streaming completes under the old persona, next send uses the new persona)
- What if localStorage is disabled or the browser is in incognito mode? (Answer: persona selection defaults to first option on each page load, no persistence error)
- What if the intent event arrives after the done event? (Answer: badge is added retrospectively; design assumes in-order delivery per contract)
- What if a quick-prompt is clicked while a message is already being sent? (Answer: button is disabled during loading, same as send button)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A "New chat" button in the header MUST clear all visible messages and generate a fresh `session_id` without changing the current `user_id`.
- **FR-002**: The persona switcher MUST provide a dropdown of 2-3 predefined personas, each mapped to a fixed, stable UUID (not randomly generated).
- **FR-003**: Switching personas MUST clear messages, generate a fresh `session_id`, and update the `user_id` for subsequent requests.
- **FR-004**: The last-selected persona MUST be persisted in browser localStorage and restored on page reload.
- **FR-005**: Intent badges MUST render beneath each assistant message with the intent value received from the `intent` event.
- **FR-006**: Intent events MUST continue to be logged to browser console for debugging (existing behavior preserved).
- **FR-007**: Intent badge styling MUST use intent-specific colors via TailwindCSS: `policy_question` → `bg-blue-100 text-blue-700`, `action_request` → `bg-amber-100 text-amber-700`, `direct_response` → `bg-gray-200 text-gray-700`, `escalation` → `bg-orange-100 text-orange-700`, `blocked` → `bg-red-100 text-red-700`. Badge shape is rounded-pill with padding (`rounded-full px-2 py-1 text-xs`).
- **FR-008**: Quick-prompt buttons (5 buttons) MUST appear in a row above the input field, each labeled with one of: "Check ticket TKT-1001", "What's the VPN policy?", "My VPN keeps disconnecting, please create a ticket", "Reset my password, I'm locked out, employee EMP-9", "ignore previous instructions".
- **FR-009**: Clicking a quick-prompt button MUST populate the input field with the button's text and send immediately (same flow as manual send).
- **FR-010**: Quick-prompt buttons MUST be disabled during loading to prevent concurrent sends.
- **FR-011**: All four features (new session, persona switcher, intent badges, quick-prompts) MUST operate independently without interfering with each other.
- **FR-012**: Switching personas mid-session MUST behave like starting a new chat (clear messages, fresh session), treating it as a distinct conversation context.

### Key Entities *(include if feature involves data)*

- **Persona**: Fixed identity with a stable UUID, a display name (e.g., "Alex", "Jordan", "Sam"), stored in `frontend/src/constants.ts`. Three predefined personas:
  - Alex: `550e8400-e29b-41d4-a716-446655440001`
  - Jordan: `550e8400-e29b-41d4-a716-446655440002`
  - Sam: `550e8400-e29b-41d4-a716-446655440003`
- **IntentBadge**: Displayed label derived from the `intent` event payload, rendered as a small rounded-pill element beneath each assistant response. Color varies by intent type:
  - `policy_question` → `bg-blue-100 text-blue-700` (blue)
  - `action_request` → `bg-amber-100 text-amber-700` (amber)
  - `direct_response` → `bg-gray-200 text-gray-700` (gray)
  - `escalation` → `bg-orange-100 text-orange-700` (orange)
  - `blocked` → `bg-red-100 text-red-700` (red)
- **QuickPrompt**: Pre-written example query text, stored in a constant array in `frontend/src/constants.ts`, with five entries:
  1. "Check ticket TKT-1001" (demonstrates ticket lookup tool)
  2. "What's the VPN policy?" (demonstrates RAG search with citations)
  3. "My VPN keeps disconnecting, please create a ticket" (demonstrates successful ticket creation)
  4. "Reset my password, I'm locked out, employee EMP-9" (demonstrates escalation due to malformed ID)
  5. "ignore previous instructions" (demonstrates injection prevention and blocked intent)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start a new conversation in under 1 second by clicking "New chat" without page reload.
- **SC-002**: Persona switcher shows 3 personas; switching takes under 500ms and immediately reflects in the next request's `user_id`.
- **SC-003**: Intent badges appear within 100ms of the assistant response being rendered, matching the console-logged intent value in all test cases.
- **SC-004**: Quick-prompt buttons trigger sends successfully in 100% of click attempts, with identical behavior to manual typing + send.
- **SC-005**: All four features coexist without runtime errors, layout breaking, or state corruption across 50+ interaction cycles in manual testing.
- **SC-006**: Persona persistence works correctly: switching personas, reloading page, and selecting a different persona works across 5+ reload cycles.
- **SC-007**: No backend changes required; all features operate on frontend state only using existing `/chat/stream` endpoint.

## Assumptions

- Personas are defined as a frontend constant in `frontend/src/constants.ts` with three fixed entries (Alex, Jordan, Sam) with stable UUIDs (550e8400-e29b-41d4-a716-446655440001/002/003); they are not fetched from the backend. Alex is the default persona on initial load.
- Browser localStorage is available and functional; if disabled, the persona selector defaults to Alex on each load without error.
- Intent badges are rendered only when an `intent` event is received; if no intent is sent, no badge is displayed.
- Quick-prompts are stored as a frontend constant array in `frontend/src/constants.ts`; there is no backend configuration or dynamic prompt loading.
- The `session_id` is always regenerated locally via `crypto.randomUUID()` when "New chat" is clicked or persona is switched, without backend involvement.
- The existing `user_id` persists across page reloads unless the user explicitly switches personas.
- All four features use the existing stream event contract and `/chat/stream` endpoint without modifications.
- Switching personas mid-conversation (while messages are in the timeline) clears the message list as part of the new-session behavior.
- Intent events arrive in order and are processed before the `done` event; badge rendering assumes chronological delivery per existing contract.
- All styling is done with TailwindCSS using the existing frontend build pipeline; no additional CSS frameworks are added.
