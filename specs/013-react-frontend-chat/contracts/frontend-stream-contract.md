# Frontend Contract: Stream Consumption and Rendering

## Endpoint Contracts Consumed (Unchanged)

### POST /chat/stream
Request JSON body:
- `user_id: string`
- `session_id: string`
- `message: string`

Response transport:
- SSE-like text stream where each event is delivered as a `data: {json}` line.
- Frontend parses line-by-line from `fetch()` `ReadableStream`.

### GET /health
- Optional informational check only.
- Does not gate message sending.
- Failures surface through the same safe error messaging approach used for stream failures.

## Event Handling Contract

### intent
- Payload: `data` string intent label.
- UI behavior: log to console for debugging only; do not render in conversation.

### token
- Payload: token text fragment.
- UI behavior: append fragment to active assistant message for live streaming effect.

### tool_call
- Payload: JSON-encoded string.
- UI behavior: parse JSON and render structured card:
  - TicketStatusCard
  - PasswordResetCard
  - TicketCreateCard
- Raw JSON must not be shown directly to users.

### error
- Payload: JSON-encoded string containing at least `message`.
- UI behavior: parse payload and render distinct error bubble showing safe `message` only.
- Raw payload text and stack traces must not be shown.

### done
- Payload: usually empty string.
- UI behavior: end active response, stop loading indicator, re-enable input.

## Stream Parser Contract
- Parser must support chunk boundaries splitting lines across multiple `ReadableStream` chunks.
- Parser must process multiple `data:` lines within one chunk.
- Non-`data:` lines are ignored safely.
- Parser completion without `done` should still return UI to a recoverable state.

## UI State Contract
- Message send flow:
  1. validate non-empty input
  2. append user message immediately
  3. append placeholder assistant message
  4. stream updates until error or done
- Loading indicator is active from send start until `done` or terminal failure.
- Session identity is stable for one page load via `crypto.randomUUID()` values.

## Out-of-Scope Contract Notes
- No backend API or schema changes.
- No authentication flow.
- No cross-session transcript retrieval UI.
- No long-term-memory inspection UI.
