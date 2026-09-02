/**
 * Stream event types and interfaces matching backend schema
 * Reference: specs/013-react-frontend-chat/contracts/frontend-stream-contract.md
 */

export type StreamEventType = 'intent' | 'token' | 'tool_call' | 'error' | 'done';

export interface StreamEventEnvelope {
  event_type: StreamEventType;
  data: string;
}

// Intent event: logged to console only
export interface IntentEvent extends StreamEventEnvelope {
  event_type: 'intent';
  data: string; // intent label
}

// Token event: streamed text fragment
export interface TokenEvent extends StreamEventEnvelope {
  event_type: 'token';
  data: string; // token text fragment
}

// Tool call event: structured tool response
export interface ToolCallEvent extends StreamEventEnvelope {
  event_type: 'tool_call';
  data: string; // JSON-encoded tool payload
}

// Error event: backend error message
export interface ErrorEvent extends StreamEventEnvelope {
  event_type: 'error';
  data: string; // JSON-encoded error payload
}

// Done event: stream completion
export interface DoneEvent extends StreamEventEnvelope {
  event_type: 'done';
  data: string; // usually empty
}
