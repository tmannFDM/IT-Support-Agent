/**
 * ChatView component for displaying conversation and message input
 * Handles message list scrolling, loading state, and new features:
 * - Feature 014: New chat button, persona selector, quick-prompts
 * Reference: specs/013-react-frontend-chat/plan.md (T010)
 *           specs/014-frontend-polish/plan.md (T011, T016, T028)
 */

import React, { useEffect, useRef } from 'react';
import { ChatMessage } from '../types/chatUi';
import { MessageBubble } from './MessageBubble';
import { PersonaSelector } from './PersonaSelector';
import { QuickPromptRow } from './QuickPromptRow';

interface ChatViewProps {
  messages: ChatMessage[];
  isLoading: boolean;
  inputValue: string;
  onInputChange: (value: string) => void;
  onSendMessage: (message?: string) => void;
  selectedPersonaId: string;
  onPersonaChange: (personaId: string) => void;
  onNewChat: () => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  isLoading,
  inputValue,
  onInputChange,
  onSendMessage,
  selectedPersonaId,
  onPersonaChange,
  onNewChat,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendClick = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSendClick();
    }
  };

  const handleQuickPrompt = (message: string) => {
    onInputChange(message);
    onSendMessage(message);
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-300 bg-gray-50 p-4">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold text-gray-800">IT Support Chat</h1>
          <div className="flex items-center gap-3">
            <PersonaSelector
              selectedPersonaId={selectedPersonaId}
              onChange={onPersonaChange}
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={onNewChat}
              disabled={isLoading}
              className="rounded-lg border border-blue-600 px-4 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:border-gray-300 disabled:text-gray-400"
            >
              New chat
            </button>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>Welcome to IT Support Chat</p>
            <p className="text-sm mt-2">
              Ask a question or describe your issue to get started
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            <MessageBubble
              role={msg.role}
              content={msg.content}
              isStreaming={msg.isStreaming}
              intentValue={msg.intentValue}
            />
            {msg.toolCard && (
              <div className="flex justify-start mb-4">
                <div className="bg-blue-50 border border-blue-200 px-4 py-3 rounded-lg max-w-md">
                  {/* Tool card will be rendered by App component */}
                  <div className="text-sm text-gray-600">
                    Tool Response: {msg.toolCard.type}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && messages.length > 0 && !messages[messages.length - 1]?.toolCard && (
          <div className="text-center text-gray-500 py-4">
            <div className="inline-block animate-spin">⟳</div>
            <p className="text-sm mt-2">Waiting for response...</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-300 p-4 bg-gray-50">
        <div className="mx-auto max-w-5xl">
          <QuickPromptRow
            isLoading={isLoading}
            onPromptClick={handleQuickPrompt}
          />
          <div className="flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Shift+Enter for new line)"
            disabled={isLoading}
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 disabled:bg-gray-100 resize-none"
            rows={3}
          />
          <button
            onClick={handleSendClick}
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            Send
          </button>
          </div>
        </div>
      </div>
    </div>
  );
};
