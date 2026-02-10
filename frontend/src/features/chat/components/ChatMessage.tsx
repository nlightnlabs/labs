import React from 'react';
import { Avatar } from '@/components/common';
import { useAppSelector } from '@/store/hooks';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const { user } = useAppSelector((state) => state.auth);
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-4 p-4 rounded-lg my-2 ${isUser ? '' : ''}`}
      style={{
        backgroundColor: isUser ? 'transparent' : 'var(--bg-secondary, #f3f4f6)',
      }}
    >
      <div className="flex-shrink-0">
        {isUser ? (
          <Avatar
            src={user?.avatar_url || user?.avatarUrl}
            alt={user?.first_name || user?.firstName || 'User'}
            size="sm"
          />
        ) : (
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ backgroundColor: 'var(--primary-500, #3b82f6)' }}
          >
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
            {isUser ? (user?.first_name || user?.firstName || 'You') : 'Assistant'}
          </span>
          <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
        <div
          className="text-sm whitespace-pre-wrap"
          style={{ color: 'var(--text-primary)' }}
        >
          {message.content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
