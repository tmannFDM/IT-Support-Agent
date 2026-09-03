/**
 * Frontend chat UI models and state types
 * Reference: specs/013-react-frontend-chat/data-model.md
 */

export type MessageRole = 'user' | 'assistant' | 'error';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  isStreaming: boolean;
  toolCard: ToolCardModel | null;
  timestamp: Date;
  intentValue?: string; // Added for Feature 014: Intent badges
}

// Tool card variants
export type ToolCardModel = 
  | { type: 'ticket_status'; data: any }
  | { type: 'password_reset'; data: any }
  | { type: 'ticket_create'; data: any }
  | { type: 'unknown'; data: any };

// Client session identity
export interface ClientSessionIdentity {
  user_id: string;
  session_id: string;
}

// Chat request payload sent to backend
export interface ChatRequestPayload {
  user_id: string;
  session_id: string;
  message: string;
}

// Chat state
export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  sessionIdentity: ClientSessionIdentity;
  inputValue: string;
}
