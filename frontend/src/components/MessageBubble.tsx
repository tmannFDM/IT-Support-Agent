/**
 * MessageBubble component for rendering chat messages
 * Supports user, assistant, and error variants
 * Reference: specs/013-react-frontend-chat/plan.md (T009)
 */

import React from 'react';
import { MessageRole } from '../types/chatUi';

interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  isStreaming?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  content,
  isStreaming = false,
}) => {
  if (role === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-xs break-words">
          {content}
        </div>
      </div>
    );
  }

  if (role === 'error') {
    return (
      <div className="flex justify-start mb-4">
        <div className="bg-red-100 text-red-800 border border-red-300 px-4 py-2 rounded-lg max-w-md break-words">
          <div className="font-semibold mb-1">Error</div>
          <div>{content}</div>
        </div>
      </div>
    );
  }

  // Assistant variant
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg max-w-md break-words">
        {content}
        {isStreaming && (
          <span className="inline-block ml-2 animate-pulse">▌</span>
        )}
      </div>
    </div>
  );
};
