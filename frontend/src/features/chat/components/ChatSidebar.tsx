import React, { useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import { useTranslation } from 'react-i18next';
import { chatApi } from '@/services/api';

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatSidebarRef {
  addSession: (session: ChatSession) => void;
  refreshSessions: () => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
}

interface ChatSidebarProps {
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onDeleteSession: (sessionId: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const ChatSidebar = forwardRef<ChatSidebarRef, ChatSidebarProps>(({
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  isOpen,
}, ref) => {
  const { t } = useTranslation();
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  // Load chat sessions on mount
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const response = await chatApi.getSessions();
        if (response.data.success) {
          setSessions(response.data.data);
        }
      } catch (error) {
        console.error('Failed to load chat sessions:', error);
      }
    };
    loadSessions();
  }, []);

  // Expose methods to parent via ref
  useImperativeHandle(ref, () => ({
    addSession: (session: ChatSession) => {
      setSessions((prev) => [session, ...prev]);
    },
    refreshSessions: async () => {
      try {
        const response = await chatApi.getSessions();
        if (response.data.success) {
          setSessions(response.data.data);
        }
      } catch (error) {
        console.error('Failed to refresh chat sessions:', error);
      }
    },
    updateSessionTitle: (sessionId: string, title: string) => {
      setSessions((prev) =>
        prev.map((session) =>
          session.id === sessionId ? { ...session, title } : session
        )
      );
    },
  }));

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await chatApi.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      onDeleteSession(sessionId);
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  // Group sessions by date
  const groupedSessions = React.useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);

    const groups: { label: string; sessions: ChatSession[] }[] = [
      { label: t('chat.today'), sessions: [] },
      { label: t('chat.yesterday'), sessions: [] },
      { label: t('chat.lastWeek'), sessions: [] },
      { label: t('chat.older'), sessions: [] },
    ];

    sessions.forEach((session) => {
      const sessionDate = new Date(session.updated_at);
      sessionDate.setHours(0, 0, 0, 0);

      if (sessionDate >= today) {
        groups[0].sessions.push(session);
      } else if (sessionDate >= yesterday) {
        groups[1].sessions.push(session);
      } else if (sessionDate >= lastWeek) {
        groups[2].sessions.push(session);
      } else {
        groups[3].sessions.push(session);
      }
    });

    return groups.filter((group) => group.sessions.length > 0);
  }, [sessions, t]);

  if (!isOpen) {
    return null;
  }

  return (
    <aside
      className="w-64 flex-shrink-0 border-r flex flex-col"
      style={{
        backgroundColor: 'var(--bg-secondary)',
        borderColor: 'var(--border-default)',
        height: '100%',
        minHeight: '100%',
      }}
    >
      {/* New Chat Button */}
      <div className="p-3 border-b" style={{ borderColor: 'var(--border-default)' }}>
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors hover:opacity-80"
          style={{
            borderColor: 'var(--border-default)',
            color: 'var(--text-primary)',
          }}
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span className="text-sm font-medium">{t('chat.newChat')}</span>
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-2">
        {groupedSessions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm" style={{ color: 'var(--text-tertiary)' }}>
              {t('chat.noChats')}
            </p>
          </div>
        ) : (
          groupedSessions.map((group) => (
            <div key={group.label} className="mb-4">
              <h3
                className="text-xs font-medium uppercase px-2 py-1"
                style={{ color: 'var(--text-tertiary)' }}
              >
                {group.label}
              </h3>
              <div className="space-y-1">
                {group.sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`group flex items-center gap-2 px-2 py-2 rounded-lg cursor-pointer transition-colors ${
                      activeSessionId === session.id ? 'bg-opacity-100' : 'hover:bg-opacity-50'
                    }`}
                    style={{
                      backgroundColor:
                        activeSessionId === session.id
                          ? 'var(--bg-secondary)'
                          : 'transparent',
                    }}
                    onClick={() => onSelectSession(session.id)}
                  >
                    <svg
                      className="w-4 h-4 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      style={{ color: 'var(--text-tertiary)' }}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                      />
                    </svg>
                    <span
                      className="flex-1 text-sm truncate"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {session.title || t('chat.untitledChat')}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteSession(session.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded transition-opacity hover:bg-opacity-80"
                      style={{ color: 'var(--text-tertiary)' }}
                      title={t('common.delete')}
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
});

export default ChatSidebar;
