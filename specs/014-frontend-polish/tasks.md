# Tasks: Frontend Polish – Demo Features (Feature 014)

**Feature Branch**: `014-frontend-polish`  
**Date**: 2026-09-02  
**Input**: Design documents from `/specs/014-frontend-polish/`

**Organization**: Tasks grouped by user story (US1–US4) to enable independent implementation and testing. All tasks are frontend-only; no backend changes required.

**Format**: `- [ ] [ID] [P?] [Story?] Description`
- `[P]` = Can run in parallel (different files, no blocking dependencies)
- `[Story]` = User story label (US1, US2, US3, US4)
- File paths are workspace-relative from `frontend/` directory

---

## Phase 1: Setup – Constants & Type Definitions

**Purpose**: Create shared data definitions (personas, quick-prompts, intent colors)

- [X] T001 Create `src/constants.ts` with Persona definitions, DEFAULT_PERSONA, and PERSONAS array (Alex, Jordan, Sam with fixed UUIDs)
- [X] T002 [P] Add QUICK_PROMPTS constant array to `src/constants.ts` with 5 pre-configured prompts and exact message text
- [X] T003 [P] Add INTENT_BADGE_COLORS mapping to `src/constants.ts` with intent-type-specific TailwindCSS color pairs (blue/amber/gray/orange/red)

**Checkpoint**: All constants defined and TypeScript-checked; ready for component implementation

---

## Phase 2: Foundational – App.tsx State & Event Handling

**Purpose**: Extend App.tsx with persona state management and intent event integration

- [X] T004 Update App.tsx imports: import PERSONAS, DEFAULT_PERSONA, QUICK_PROMPTS, INTENT_BADGE_COLORS from `./constants`
- [X] T005 Add new state to App.tsx: `selectedPersonaId` initialized from localStorage or DEFAULT_PERSONA.id
- [X] T006 Add new state to App.tsx: `sessionIdentity` updated to use `selectedPersonaId` as `user_id`
- [X] T007 Modify App.tsx: update `handleSendMessage` to attach `sessionIdentity.user_id` and `sessionIdentity.session_id` to requests (verify existing behavior maintained)
- [X] T008 Modify App.tsx `handleStreamEvent`: extract and attach `intent` value from `intent` event to ChatMessage as `intentValue` property (alongside existing console.log)
- [X] T009 Create `updatePersona(personaId: string)` function in App.tsx: set selectedPersonaId, update localStorage, clear messages, regenerate session_id, update sessionIdentity.user_id

**Checkpoint**: App state extended with persona management and intent tracking; ready for UI component integration

---

## Phase 3: User Story 1 – New Chat Button (Priority: P1)

**Goal**: Enable users to start a fresh conversation while preserving their current persona/user_id

**Independent Test**: Click "New chat" → verify message list clears → send message → verify session_id changed but user_id unchanged

### Implementation for User Story 1

- [X] T010 [US1] Create `handleNewChat()` function in App.tsx: clears messages array, regenerates session_id, preserves user_id (calls setMessages([]) and updates sessionIdentity with new session_id)
- [X] T011 [US1] Modify ChatView.tsx: Add "New chat" button to header (before or next to title), styled with TailwindCSS button classes
- [X] T012 [US1] Wire ChatView "New chat" button: pass `handleNewChat` as onClick handler from App.tsx props

**Checkpoint**: New chat button functional; clears messages and regenerates session_id while preserving user_id

---

## Phase 4: User Story 2 – Persona Switcher (Priority: P1)

**Goal**: Enable users to switch between fixed personas, each with stable UUID, clearing messages and session on switch

**Independent Test**: Switch persona → verify messages clear → send message → verify user_id matches new persona's UUID → reload page → verify persona persists

### Implementation for User Story 2

- [X] T013 [P] [US2] Create `PersonaSelector` component (or inline in ChatView): dropdown/select menu rendering PERSONAS array with displayName as label, id as value
- [X] T014 [P] [US2] Style PersonaSelector with TailwindCSS: standard dropdown styling (consistent with existing button/input styling)
- [X] T015 [US2] Add onChange handler to PersonaSelector: calls `updatePersona(selectedId)` from App.tsx
- [X] T016 [US2] Integrate PersonaSelector into ChatView.tsx header: replace or supplement existing user_id display with persona dropdown
- [X] T017 [US2] Update App.tsx: pass `selectedPersonaId` and `updatePersona` as props to ChatView for selector integration
- [X] T018 [US2] Verify localStorage persistence: confirm `selectedPersonaId` is read on App mount and written on persona change

**Checkpoint**: Persona switcher functional; switching clears messages, changes user_id, regenerates session_id, and persists across page reloads

---

## Phase 5: User Story 3 – Intent Badges (Priority: P2)

**Goal**: Render intent classification as colored badges beneath assistant messages

**Independent Test**: Send message with intent → verify badge appears beneath response → verify console still logs intent → verify badge color matches intent type

### Implementation for User Story 3

- [X] T019 [P] [US3] Create new component `src/components/IntentBadge.tsx`: accepts `intentValue` prop, renders pill-shaped badge using TailwindCSS classes from INTENT_BADGE_COLORS mapping
- [X] T020 [P] [US3] IntentBadge styling: use `rounded-full px-2 py-1 text-xs` base classes + intent-specific color classes from constant
- [X] T021 [P] [US3] Modify MessageBubble.tsx: check for `message.intentValue` property; if present and non-null, render IntentBadge component below message content
- [X] T022 [US3] Verify badge fallback: confirm no badge renders if `intentValue` is null/undefined (hide completely, no "Unknown" placeholder)
- [ ] T023 [US3] Test intent badge integration: send messages with various intents (policy_question, action_request, blocked, etc.) and verify correct colors render (reference quickstart.md Scenario 4)

**Checkpoint**: Intent badges render correctly with intent-specific colors; existing console logging preserved

---

## Phase 6: User Story 4 – Quick-Prompt Buttons (Priority: P2)

**Goal**: Provide 5 pre-configured example buttons that populate input and send immediately

**Independent Test**: Click quick-prompt button → verify input populated → verify message sent immediately → verify disabled during loading

### Implementation for User Story 4

- [X] T024 [P] [US4] Create new component `src/components/QuickPromptRow.tsx`: renders QUICK_PROMPTS array as a row of 5 buttons (flex layout, TailwindCSS button styling)
- [X] T025 [P] [US4] QuickPromptRow styling: buttons in horizontal row above input field, spaced evenly (gap-2 or similar), consistent with form styling
- [X] T026 [US4] Add `disabled={isLoading}` prop to QuickPromptRow buttons: pass `isLoading` from App.tsx to prevent concurrent sends while response pending
- [X] T027 [US4] Create `handleQuickPromptClick(prompt: QuickPrompt)` in App.tsx or ChatView: sets inputValue to prompt.message and calls handleSendMessage immediately
- [X] T028 [US4] Wire QuickPromptRow to ChatView: render QuickPromptRow above input textarea, pass `isLoading` and `onPromptClick={handleQuickPromptClick}` as props
- [ ] T029 [US4] Test quick-prompt flow: click each of 5 buttons and verify message sends, input behavior correct, and disabled state during loading (reference quickstart.md Scenario 5)

**Checkpoint**: Quick-prompt buttons functional; all 5 buttons send messages correctly, disabled during loading, text replaces manual input

---

## Phase 7: Integration & End-to-End Validation

**Purpose**: Verify all 4 features work together without interference; cross-feature state management

- [X] T030 [P] Integration: Verify new session button preserves persona and user_id (T010–T012 + T013–T018)
- [X] T031 [P] Integration: Verify persona switching triggers new session behavior (clear messages, regen session_id, T010 + T013–T018)
- [ ] T032 [P] Integration: Verify intent badges persist across all feature interactions (new chat, persona switch, quick-prompts)
- [X] T033 [P] Integration: Verify quick-prompt buttons work with all personas and after new chat
- [ ] T034 [P] Robustness: Run manual 50+ interaction cycles (reference quickstart.md Scenario 6) combining all features
- [X] T035 [P] Browser DevTools verification: inspect localStorage, console logs, network requests (session_id and user_id values)
- [ ] T036 [P] Performance verification: confirm <1s new chat, <500ms persona switch, <100ms badge render, 100% quick-prompt success
- [ ] T037 Cross-feature testing: Verify no runtime errors, layout corruption, or state inconsistencies across 50+ cycles

**Checkpoint**: All 4 features coexist and function correctly; success criteria SC-001 through SC-007 verified

---

## Phase 8: Polish & Documentation

**Purpose**: Final cleanup, type safety, and documentation

- [X] T038 TypeScript: Run `tsc --noEmit` in frontend/ directory and fix any type errors or warnings
- [X] T039 Code review: Verify no unintended modifications to Feature 013 components (ChatView, MessageBubble, backend, streaming logic)
- [X] T040 Update frontend README.md or docs: Document new features (persona switcher, quick-prompts, intent badges) for future developers
- [X] T041 Verify all constants exported from `constants.ts` and used correctly in components (no hardcoded values in JSX)

**Checkpoint**: All code polished, type-safe, documented; Feature 014 ready for deployment

---

## Success Criteria Verification

**SC-001**: ✓ T010–T012 (New chat <1s)  
**SC-002**: ✓ T013–T018 (Persona switch <500ms, user_id updated)  
**SC-003**: ✓ T019–T023 (Intent badges <100ms, correct colors)  
**SC-004**: ✓ T024–T029 (Quick-prompts 100% success)  
**SC-005**: ✓ T034–T037 (50+ cycles, no errors)  
**SC-006**: ✓ T018, T035 (Persona persistence, localStorage)  
**SC-007**: ✓ All tasks (Frontend-only, no backend changes)

---

## Dependencies & Parallelization

**Phase 1 (T001–T003)**: No dependencies; can run in parallel  
**Phase 2 (T004–T009)**: Depends on Phase 1; sequential  
**Phase 3 (T010–T012)**: Depends on Phase 2; can run after T009  
**Phase 4 (T013–T018)**: Depends on Phase 2; can run in parallel with Phase 3  
**Phase 5 (T019–T023)**: Depends on Phase 2; can run in parallel with Phase 3 & 4  
**Phase 6 (T024–T029)**: Depends on Phase 2; can run in parallel with Phase 3, 4, 5  
**Phase 7 (T030–T037)**: Depends on Phase 3–6; sequential  
**Phase 8 (T038–T041)**: Depends on Phase 7; final polish  

**Recommended Execution Order**:
1. Phase 1 (setup)
2. Phase 2 (foundation)
3. Phases 3–6 in parallel (independent user story implementation)
4. Phase 7 (integration)
5. Phase 8 (polish)

**Estimated Total Tasks**: 41 tasks  
**Estimated Complexity**: LOW (frontend-only, no backend, existing patterns)  
**Estimated Time**: 2–3 hours (experienced React developer)

---

## Notes

- All file paths are workspace-relative within `frontend/` directory
- No backend, streaming client, or tool card modifications required
- Feature 013 components remain unchanged except where necessary (MessageBubble for intent badge, ChatView for new UI elements)
- All styling uses existing TailwindCSS classes; no new CSS files added
- All state management uses React hooks; no new state management library required
- Testing is manual end-to-end per quickstart.md scenarios (no automated test suite for frontend)
