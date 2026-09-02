/**
 * Tool payload interfaces mirroring backend schemas
 * Reference: specs/013-react-frontend-chat/data-model.md
 */

// Ticket Status Response
export interface TicketStatusPayload {
  ticket_id: string;
  status: string;
  priority: string;
  category: string;
  summary: string;
}

// Password Reset Response
export interface PasswordResetPayload {
  status: string;
  temporary_password_note: string;
  escalation_reason: string | null;
}

// Ticket Creation Response
export interface TicketCreatePayload {
  ticket_id: string;
  category: string;
  priority: string;
  status: string;
}

// Union type for all tool payloads
export type ToolPayload = 
  | TicketStatusPayload 
  | PasswordResetPayload 
  | TicketCreatePayload;

// Error payload from backend
export interface ErrorPayload {
  message: string;
  code?: string;
}

// Type guards
export function isTicketStatusPayload(data: unknown): data is TicketStatusPayload {
  const obj = data as any;
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.ticket_id === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.priority === 'string' &&
    typeof obj.category === 'string' &&
    typeof obj.summary === 'string'
  );
}

export function isPasswordResetPayload(data: unknown): data is PasswordResetPayload {
  const obj = data as any;
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.status === 'string' &&
    typeof obj.temporary_password_note === 'string' &&
    (obj.escalation_reason === null || typeof obj.escalation_reason === 'string')
  );
}

export function isTicketCreatePayload(data: unknown): data is TicketCreatePayload {
  const obj = data as any;
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.ticket_id === 'string' &&
    typeof obj.category === 'string' &&
    typeof obj.priority === 'string' &&
    typeof obj.status === 'string'
  );
}

export function isErrorPayload(data: unknown): data is ErrorPayload {
  const obj = data as any;
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.message === 'string'
  );
}
