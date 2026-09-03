/**
 * MessageBubble component for rendering chat messages
 * Supports user, assistant, and error variants
 * Reference: specs/013-react-frontend-chat/plan.md (T009)
 */

import React from 'react';
import { MessageRole } from '../types/chatUi';
import { IntentBadge } from './IntentBadge';

interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  isStreaming?: boolean;
  intentValue?: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  content,
  isStreaming = false,
  intentValue,
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
    <div className="mb-4 flex justify-start">
      <div className="max-w-md break-words">
        <div className="rounded-lg bg-gray-100 px-4 py-2 text-gray-900">
          {content}
          {isStreaming && (
            <span className="ml-2 inline-block animate-pulse">▌</span>
          )}
        </div>
        {intentValue && <IntentBadge intentValue={intentValue} />}
      </div>
    </div>
  );
};
