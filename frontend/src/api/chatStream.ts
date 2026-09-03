/**
 * Chat stream client with ReadableStream parser
 * Handles POST to /chat/stream and parses SSE-style data: lines
 * Reference: specs/013-react-frontend-chat/contracts/frontend-stream-contract.md
 */

import {
  StreamEventEnvelope,
  StreamEventType,
} from '../types/events';
import {
  isTicketStatusPayload,
  isPasswordResetPayload,
  isTicketCreatePayload,
  isErrorPayload,
  ErrorPayload,
} from '../types/toolPayloads';
import { ChatRequestPayload } from '../types/chatUi';

/**
 * Parse JSON payload safely without throwing
 */
function safeJsonParse(jsonStr: string): any {
  try {
    return JSON.parse(jsonStr);
  } catch (e) {
    console.error('Failed to parse JSON:', jsonStr, e);
    return null;
  }
}

/**
 * Parse a data: line and return the decoded event
 */
export function parseEventLine(line: string): StreamEventEnvelope | null {
  if (!line.startsWith('data:')) {
    return null;
  }

  const jsonStr = line.slice(5).trim();
  if (!jsonStr) {
    return null;
  }

  const parsed = safeJsonParse(jsonStr);
  if (!parsed || !parsed.event_type) {
    return null;
  }

  return {
    event_type: parsed.event_type as StreamEventType,
    data: parsed.data ?? '',
  };
}

/**
 * Stream response parser callback type
 */
export type StreamEventCallback = (event: StreamEventEnvelope) => void;

/**
 * Parse ReadableStream chunks and invoke callback for each event
 */
export async function parseStreamResponse(
  response: Response,
  onEvent: StreamEventCallback
): Promise<void> {
  if (!response.body) {
    throw new Error('Response has no body');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // Process any remaining buffer content
        if (buffer.trim()) {
          const event = parseEventLine(buffer);
          if (event) {
            onEvent(event);
          }
        }
        break;
      }

      // Append chunk to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete lines
      const lines = buffer.split('\n');

      // Keep the last incomplete line in the buffer
      buffer = lines[lines.length - 1];

      // Process all complete lines
      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const event = parseEventLine(line);
        if (event) {
          onEvent(event);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Send chat message and stream responses
 */
export async function postChatStream(
  payload: ChatRequestPayload,
  onEvent: StreamEventCallback,
  onError: (error: Error) => void
): Promise<void> {
  try {
    const response = await fetch('/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    await parseStreamResponse(response, onEvent);
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    onError(err);
  }
}

/**
 * Safe parser for error payloads
 */
export function parseErrorPayload(data: string): ErrorPayload {
  if (!data.trim()) {
    return {
      message: 'An error occurred. Please try again.',
      code: 'UNKNOWN_ERROR',
    };
  }

  const parsed = safeJsonParse(data);

  if (isErrorPayload(parsed) && parsed.message.trim()) {
    return parsed;
  }

  // Fallback to safe message
  return {
    message: 'An error occurred. Please try again.',
    code: 'UNKNOWN_ERROR',
  };
}

/**
 * Safe parser for tool_call payloads
 */
export function parseToolCallPayload(data: string): any {
  const parsed = safeJsonParse(data);

  if (!parsed) {
    return null;
  }

  // Identify tool type by field signature
  if (isTicketStatusPayload(parsed)) {
    return { type: 'ticket_status', data: parsed };
  }

  if (isPasswordResetPayload(parsed)) {
    return { type: 'password_reset', data: parsed };
  }

  if (isTicketCreatePayload(parsed)) {
    return { type: 'ticket_create', data: parsed };
  }

  // Unknown tool type
  return { type: 'unknown', data: parsed };
}
