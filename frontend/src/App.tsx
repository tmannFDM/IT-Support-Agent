/**
 * Main App component orchestrating chat state and stream handling
 * Implements:
 * - T011: App state for conversation timeline
 * - T012: Send handler with token streaming
 * - T013: Done event handling
 * - T017: Tool card rendering
 * - T018: Intent event logging
 * - T019: Error event display
 * - T020-T023: Session identity and input validation
 * Reference: specs/013-react-frontend-chat/plan.md
 */

import { useEffect, useState } from 'react';
import { ChatView } from './components/ChatView';
import { TicketStatusCard } from './components/TicketStatusCard';
import { PasswordResetCard } from './components/PasswordResetCard';
import { TicketCreateCard } from './components/TicketCreateCard';
import {
  ChatMessage,
  ChatState,
  ChatRequestPayload,
} from './types/chatUi';
import { StreamEventEnvelope } from './types/events';
import {
  postChatStream,
  parseErrorPayload,
  parseToolCallPayload,
} from './api/chatStream';
import {
  PERSONAS,
  DEFAULT_PERSONA,
} from './constants';

function App() {
  const [selectedPersonaId, setSelectedPersonaId] = useState<string>(() => {
    try {
      const storedPersonaId = localStorage.getItem('selectedPersonaId');
      return storedPersonaId !== null && PERSONAS.some((persona) => persona.id === storedPersonaId)
        ? storedPersonaId
        : DEFAULT_PERSONA.id;
    } catch {
      return DEFAULT_PERSONA.id;
    }
  });

  const [state, setState] = useState<ChatState>(() => ({
    messages: [],
    isLoading: false,
    sessionIdentity: {
      user_id: selectedPersonaId,
      session_id: crypto.randomUUID(),
    },
    inputValue: '',
  }));

  // Generate session identity on mount
  useEffect(() => {
    console.log('Session established:', state.sessionIdentity);
  }, [state.sessionIdentity]);

  /**
   * Handle stream events from backend
   */
  const handleStreamEvent = (event: StreamEventEnvelope) => {
    const { event_type, data } = event;

    setState((prev) => {
      const messages = [...prev.messages];
      const lastMessage = messages[messages.length - 1];

      switch (event_type) {
        case 'intent':
          // Attach intent value to last assistant message and log for debugging
          console.log('[intent]', data);
          if (lastMessage && lastMessage.role === 'assistant') {
            messages[messages.length - 1] = {
              ...lastMessage,
              intentValue: data,
            };
          }
          return { ...prev, messages };
        
        case 'token': {
            if (lastMessage && lastMessage.role === 'assistant') {
            const separator = lastMessage.content ? ' ' : '';
            messages[messages.length - 1] = {
                ...lastMessage,
                content: lastMessage.content + separator + data,
            };
            }
            return { ...prev, messages };
        }
        
        case 'tool_call': {
            const toolCard = parseToolCallPayload(data);
            if (lastMessage && lastMessage.role === 'assistant' && toolCard) {
                messages[messages.length - 1] = { ...lastMessage, toolCard };
             }
            return { ...prev, messages };
        }

        case 'error':
          // Render error message
          const errorPayload = parseErrorPayload(data);
          messages.push({
            id: `error-${Date.now()}`,
            role: 'error',
            content: errorPayload.message,
            isStreaming: false,
            toolCard: null,
            timestamp: new Date(),
          });
          return { ...prev, messages, isLoading: false };

        case 'done': {
            if (lastMessage && lastMessage.role === 'assistant') {
                messages[messages.length - 1] = { ...lastMessage, isStreaming: false };
            }
            return { ...prev, isLoading: false };
        }

        default:
          return prev;
      }
    });
  };

  /**
   * Handle stream errors
   */
  const handleStreamError = (error: Error) => {
    console.error('Stream error:', error);

    setState((prev) => {
      const messages = [...prev.messages];
      messages.push({
        id: `error-${Date.now()}`,
        role: 'error',
        content: error.message || 'Failed to get response. Please try again.',
        isStreaming: false,
        toolCard: null,
        timestamp: new Date(),
      });
      return { ...prev, messages, isLoading: false };
    });
  };

  const updatePersona = (personaId: string) => {
    if (!PERSONAS.some((persona) => persona.id === personaId)) {
      return;
    }

    setSelectedPersonaId(personaId);
    try {
      localStorage.setItem('selectedPersonaId', personaId);
    } catch {
      // Persistence is optional when browser storage is unavailable.
    }
    setState((prev) => ({
      ...prev,
      messages: [],
      sessionIdentity: {
        user_id: personaId,
        session_id: crypto.randomUUID(),
      },
      inputValue: '',
    }));
  };

  const handleNewChat = () => {
    setState((prev) => ({
      ...prev,
      messages: [],
      sessionIdentity: {
        user_id: prev.sessionIdentity.user_id,
        session_id: crypto.randomUUID(),
      },
      inputValue: '',
    }));
  };

  /**
   * Send message and start streaming
   */
  const handleSendMessage = (message = state.inputValue) => {
    const trimmedInput = message.trim();

    // Validate non-empty input
    if (!trimmedInput) {
      console.warn('Empty message rejected');
      return;
    }

    if (state.isLoading) {
      return;
    }

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmedInput,
      isStreaming: false,
      toolCard: null,
      timestamp: new Date(),
    };

    // Create pending assistant message
    const assistantMessage: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      isStreaming: true,
      toolCard: null,
      timestamp: new Date(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage, assistantMessage],
      isLoading: true,
      inputValue: '',
    }));

    // Send request to backend
    const payload: ChatRequestPayload = {
      user_id: state.sessionIdentity.user_id,
      session_id: state.sessionIdentity.session_id,
      message: trimmedInput,
    };

    postChatStream(payload, handleStreamEvent, handleStreamError);
  };

  /**
   * Render tool card based on type
   */
  const renderToolCard = (toolCard: any) => {
    if (!toolCard) return null;

    switch (toolCard.type) {
      case 'ticket_status':
        return <TicketStatusCard data={toolCard.data} />;
      case 'password_reset':
        return <PasswordResetCard data={toolCard.data} />;
      case 'ticket_create':
        return <TicketCreateCard data={toolCard.data} />;
      default:
        return (
          <div className="bg-gray-100 border border-gray-300 rounded-lg p-4 max-w-md">
            <div className="text-sm text-gray-600 font-semibold mb-2">
              Unknown Tool Response
            </div>
            <pre className="text-xs bg-white p-2 rounded border border-gray-200 overflow-auto">
              {JSON.stringify(toolCard.data, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div className="h-screen">
      <ChatView
        messages={state.messages.map((msg) => ({
          ...msg,
          // Override tool card rendering in ChatView if needed
          toolCard: msg.toolCard,
        }))}
        isLoading={state.isLoading}
        inputValue={state.inputValue}
        onInputChange={(value) =>
          setState((prev) => ({ ...prev, inputValue: value }))
        }
        onSendMessage={handleSendMessage}
        selectedPersonaId={selectedPersonaId}
        onPersonaChange={updatePersona}
        onNewChat={handleNewChat}
      />

      {/* Render tool cards inline */}
      <div className="hidden">
        {state.messages.map((msg) =>
          msg.toolCard ? (
            <div key={msg.id} className="mb-4">
              {renderToolCard(msg.toolCard)}
            </div>
          ) : null
        )}
      </div>
    </div>
  );
}

export default App;
