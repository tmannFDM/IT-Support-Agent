# Quickstart: Validate React Frontend Chat Experience

## Prerequisites
- Node.js 20 LTS (or compatible current LTS)
- Python backend already runnable in this repository
- Existing backend `/chat/stream` and `/health` endpoints available

## Implementation Summary
✓ **COMPLETED**
- Vite `react-ts` scaffold in top-level `frontend/`
- TailwindCSS via standard PostCSS-integrated setup
- `frontend/src/api/chatStream.ts` stream client for POST + ReadableStream SSE parsing
- `frontend/src/types/` interfaces (events.ts, toolPayloads.ts, chatUi.ts) matching backend schemas
- `frontend/src/components/` chat UI components:
  - ChatView.tsx: Message list, input, loading indicator
  - MessageBubble.tsx: User, assistant, and error variants
  - TicketStatusCard.tsx: Ticket status tool response
  - PasswordResetCard.tsx: Password reset tool response
  - TicketCreateCard.tsx: Ticket creation tool response
- `frontend/src/App.tsx`: Session identity generation, state orchestration, stream handler

## Setup and run
1. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start backend service**:
   Follow the backend documentation to start the Python service on port 8000 (or configured port).

3. **Start frontend dev server**:
   ```bash
   cd frontend
   npm run dev
   ```
   The dev server will be available at `http://localhost:5173/`.

4. **Open in browser**:
   Navigate to `http://localhost:5173/` in your web browser.

## Build for production
```bash
cd frontend
npm run build
# Output will be in frontend/dist/
```

## Architecture Overview

### Frontend Structure
```
frontend/
├── src/
│   ├── api/chatStream.ts          # Stream client and parser
│   ├── types/
│   │   ├── events.ts              # Stream event envelopes
│   │   ├── toolPayloads.ts        # Tool response schemas
│   │   └── chatUi.ts              # Chat state and message models
│   ├── components/
│   │   ├── ChatView.tsx           # Main chat interface
│   │   ├── MessageBubble.tsx      # Message rendering
│   │   ├── TicketStatusCard.tsx   # Ticket status card
│   │   ├── PasswordResetCard.tsx  # Password reset card
│   │   └── TicketCreateCard.tsx   # Ticket creation card
│   ├── App.tsx                    # Main component & orchestration
│   ├── main.tsx                   # React entry point
│   └── index.css                  # Tailwind styles
├── index.html                     # HTML template
├── vite.config.ts                 # Vite configuration
├── tailwind.config.ts             # Tailwind CSS config
├── postcss.config.js              # PostCSS config
└── package.json                   # Dependencies
```

### Key Features Implemented

**Phase 1: Setup**
- ✓ Vite React TypeScript scaffold with build configuration
- ✓ TailwindCSS with PostCSS integration (not CDN)

**Phase 2: Foundational**
- ✓ TypeScript interfaces for stream events (intent, token, tool_call, error, done)
- ✓ Tool payload interfaces with type guards (TicketStatus, PasswordReset, TicketCreate)
- ✓ Stream parser: fetch POST + ReadableStream chunked reader with line buffering
- ✓ Safe JSON parsing with fallbacks for malformed payloads

**Phase 3: User Story 1 - Streamed Chat**
- ✓ MessageBubble: User, assistant, and error variants with streaming indicator
- ✓ ChatView: Message timeline, auto-scroll, input field, send button
- ✓ App state: Conversation messages, loading indicator, input value
- ✓ Send handler: User message echo, pending assistant placeholder, token accumulation
- ✓ Done handler: Response finalization, loading reset, input re-enable

**Phase 4: User Story 2 - Structured Actions**
- ✓ TicketStatusCard: Displays ticket ID, status, priority, category, summary
- ✓ PasswordResetCard: Shows reset status, temporary password note, escalation reason
- ✓ TicketCreateCard: Shows created ticket ID, category, priority, success confirmation
- ✓ Safe error display: Error bubble with message only (no raw JSON/stack traces)
- ✓ Intent logging: Logged to browser console for debugging (not rendered)

**Phase 5: User Story 3 - Session Identity**
- ✓ User/session ID generation: `crypto.randomUUID()` on app mount
- ✓ Included in every POST request body
- ✓ Input validation: Client-side prevention of empty/whitespace-only messages
- ✓ Chronological message ordering with auto-scroll on update

## Manual Validation Scenarios

### Scenario A: Basic streamed response
**Test**: Enter a normal question and submit.

Expected behavior:
- ✓ User message appears immediately in chat view
- ✓ Assistant response starts streaming with cursor animation
- ✓ Tokens accumulate in real-time as they arrive from backend
- ✓ Loading indicator visible while streaming
- ✓ Send button disabled during stream
- ✓ Done event completes response, stops loading, re-enables input

**Validation steps**:
1. Type "What is the password reset procedure?" and click Send
2. Confirm user message appears instantly on the right (blue bubble)
3. Observe assistant token stream in real-time on the left (gray bubble with cursor)
4. Wait for done event and confirm input re-enabled

---

### Scenario B: Tool card rendering
**Test**: Trigger backend tool responses for each action type.

Expected behavior:
- ✓ TicketStatusCard renders with ticket ID, status badge, priority, category, summary
- ✓ PasswordResetCard renders with reset status, temp password note, escalation flag
- ✓ TicketCreateCard renders with new ticket ID, category, priority, success checkmark
- ✓ Cards display with appropriate color coding (green=success, yellow=pending, red=escalated)
- ✓ Raw JSON payload never visible to user

**Validation steps**:
1. Trigger a ticket status lookup (backend triggers tool_call event)
2. Confirm TicketStatusCard renders with all fields populated
3. Trigger password reset (backend triggers tool_call event)
4. Confirm PasswordResetCard renders appropriately (escalated or approved)
5. Trigger ticket creation (backend triggers tool_call event)
6. Confirm TicketCreateCard renders with success state

---

### Scenario C: Policy response with citations
**Test**: Ask a policy question that returns source citations.

Expected behavior:
- ✓ Answer text streams and displays in assistant bubble
- ✓ Citation format preserved as part of assistant message
- ✓ No special citation UI component needed (backend sends as part of token stream)
- ✓ Full answer including citations visible in conversation timeline

**Validation steps**:
1. Type "What is the password policy?" and submit
2. Observe assistant response streams with citation format included
3. Confirm full text including citations is visible and readable
4. Note that citations are rendered as part of the streaming message

---

### Scenario D: Error handling and blocked messages
**Test**: Send blocked/injection attempts and network failures.

Expected behavior:
- ✓ Prompt injection attempts caught by backend
- ✓ Backend sends error event with safe message
- ✓ Error bubble displays message text only (distinct from assistant bubbles)
- ✓ No raw JSON, stack traces, or internal details shown
- ✓ Error bubbles appear in red with error styling
- ✓ UI remains usable for retry after error

**Validation steps**:
1. Send a known blocked/injection message (configured in backend)
2. Confirm error event triggers, error bubble appears in red
3. Verify error message is safe/user-friendly
4. Try another message after error - confirm UI is still responsive

---

### Scenario E: Empty input and network failure
**Test**: Edge cases and error paths.

Expected behavior:
- ✓ Whitespace-only input blocked client-side (button disabled, no request sent)
- ✓ Network failures (backend down) caught by fetch handler
- ✓ Fetch errors displayed via same error-display path as backend errors
- ✓ Error message indicates "failed to get response"
- ✓ UI remains responsive for retry after network error

**Validation steps**:
1. Click Send without typing - button should be disabled
2. Type only whitespace ("   ") and try Send - still disabled
3. Type valid message and send while backend is stopped/unavailable
4. Confirm fetch error surfaces as error bubble
5. Restart backend and retry the message - should work

---

## Full Walkthrough Target

Perform one end-to-end session covering all backend stages:

1. **Session initialization**: Open frontend, observe unique user/session IDs in browser console
2. **Basic chat**: Ask a normal question → observe streaming response
3. **Tool usage**: Trigger one tool action → confirm tool card renders (not JSON)
4. **Policy query**: Ask a policy question → confirm citations appear in response
5. **Blocked attempt**: Send a blocked message → confirm safe error display
6. **Recovery**: Send a valid message after error → confirm UI fully recovers

Expected outcome:
- ✓ End-to-end chat flow works without backend modifications
- ✓ All stream event types (token, tool_call, error, done) handled correctly
- ✓ Tool responses render as structured cards, not raw JSON
- ✓ Error handling is safe and user-friendly
- ✓ Session identity stable for entire page load
- ✓ UI remains responsive throughout all scenarios

## Manual Validation Scenario A: Basic streamed response
1. Enter a non-empty normal question and submit.

Expected:
- User message appears immediately.
- Assistant message streams token-by-token.
- Done event ends loading and re-enables input.

## Manual Validation Scenario B: Tool card rendering
1. Trigger ticket status flow.
2. Trigger password reset flow.
3. Trigger ticket creation flow.

Expected:
- Each tool response renders as its structured card variant.
- Raw JSON payload is not shown.

## Manual Validation Scenario C: Policy response with citations
1. Ask a policy question that returns source citations.

Expected:
- Answer text displays in assistant bubble.
- Citation text remains visible as part of answer output.

## Manual Validation Scenario D: Injection/blocked error display
1. Send a known blocked/prompt-injection style message.

Expected:
- Distinct error bubble appears with safe message text.
- No raw JSON and no stack trace shown.

## Manual Validation Scenario E: Empty input and network failure handling
1. Try submitting whitespace-only input.
2. Simulate backend unavailability and send a request.

Expected:
- Empty input is blocked client-side without crash.
- Send failure appears via the same user-safe error display path.
- UI remains usable for retries.

## Full walkthrough target
Perform one end-to-end walkthrough covering all existing backend stages through the frontend chat UI to confirm compatibility without backend modifications.
