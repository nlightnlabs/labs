import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { ChatMessage, Message } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatSidebar, ChatSidebarRef } from './ChatSidebar';
import { chatApi } from '@/services/api';

export const ChatPage: React.FC = () => {
  const { t } = useTranslation();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sidebarRef = useRef<ChatSidebarRef>(null);
  const isSendingRef = useRef(false);

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const hasMessages = messages.length > 0;

  // Scroll to bottom when messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load messages when active session changes
  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      return;
    }

    // Skip loading if we're in the middle of sending a message
    // This prevents duplicate messages when creating a new session
    if (isSendingRef.current) {
      return;
    }

    const loadMessages = async () => {
      try {
        const response = await chatApi.getMessages(activeSessionId);
        if (response.data.success) {
          setMessages(response.data.data);
        }
      } catch (error) {
        console.error('Failed to load messages:', error);
      }
    };
    loadMessages();
  }, [activeSessionId]);

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  const handleDeleteSession = (sessionId: string) => {
    if (activeSessionId === sessionId) {
      setActiveSessionId(null);
      setMessages([]);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    isSendingRef.current = true;

    try {
      let sessionId = activeSessionId;

      // Create new session if none active
      if (!sessionId) {
        const sessionResponse = await chatApi.createSession({
          title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
        });
        if (sessionResponse.data.success) {
          sessionId = sessionResponse.data.data.id;
          setActiveSessionId(sessionId);
          sidebarRef.current?.addSession(sessionResponse.data.data);
        }
      }

      // Send message and get response
      const response = await chatApi.sendMessage(sessionId!, content);
      if (response.data.success) {
        const assistantMessage: Message = {
          id: response.data.data.id,
          role: 'assistant',
          content: response.data.data.content,
          timestamp: response.data.data.timestamp,
        };
        setMessages((prev) => {
          // Update the user message with real ID and add assistant response
          const updated = prev.map((m) =>
            m.id === userMessage.id
              ? { ...m, id: response.data.data.user_message_id }
              : m
          );
          return [...updated, assistantMessage];
        });

        // Update sidebar with LLM-generated topic title for first message
        if (response.data.data.is_first_message && response.data.data.topic) {
          sidebarRef.current?.updateSessionTitle(sessionId!, response.data.data.topic);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Show error message
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: t('chat.errorSending'),
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
      isSendingRef.current = false;
    }
  };

  return (
    <div className="flex h-full min-h-0 -mx-6 -my-6" style={{ height: 'calc(100vh - 64px)' }}>
      {/* Chat History Sidebar */}
      <ChatSidebar
        ref={sidebarRef}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Header */}
        <div
          className="flex items-center justify-between px-4 py-3 border-b flex-shrink-0"
          style={{ borderColor: 'var(--border-default)' }}
        >
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg transition-colors hover:bg-opacity-80"
              style={{ backgroundColor: 'var(--bg-secondary)' }}
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                style={{ color: 'var(--text-secondary)' }}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              {t('chat.title')}
            </h1>
          </div>
        </div>

        {/* Chat Content Area - Single container with animated layout */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {/* Input Container - Animated position */}
          <div
            className="w-full transition-all duration-300 ease-in-out"
            style={{
              position: hasMessages ? 'relative' : 'absolute',
              top: hasMessages ? 0 : '50%',
              left: hasMessages ? 0 : '50%',
              transform: hasMessages ? 'none' : 'translate(-50%, -50%)',
              padding: hasMessages ? '1rem' : '0 2rem',
              borderBottom: hasMessages ? '1px solid var(--border-default)' : 'none',
              zIndex: 10,
            }}
          >
            <div
              className="mx-auto transition-all duration-300 ease-in-out"
              style={{
                maxWidth: hasMessages ? '48rem' : '42rem',
                width: '100%',
              }}
            >
              {/* Welcome content - fades out when messages exist */}
              <div
                className="transition-all duration-300 ease-in-out overflow-hidden"
                style={{
                  maxHeight: hasMessages ? 0 : '200px',
                  opacity: hasMessages ? 0 : 1,
                  marginBottom: hasMessages ? 0 : '1.5rem',
                }}
              >
                <div className="flex flex-col items-center">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center mb-4"
                    style={{ backgroundColor: 'var(--primary-100, #dbeafe)' }}
                  >
                    <svg
                      className="w-8 h-8"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      style={{ color: 'var(--primary-500, #3b82f6)' }}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                      />
                    </svg>
                  </div>
                  <h2
                    className="text-xl font-semibold mb-2"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {t('chat.welcome')}
                  </h2>
                  <p
                    className="text-center max-w-md"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {t('chat.welcomeDescription')}
                  </p>
                </div>
              </div>

              {/* Chat Input */}
              <ChatInput onSend={handleSendMessage} isLoading={isLoading} />

              {/* Suggestion Buttons - fade out when messages exist */}
              <div
                className="transition-all duration-300 ease-in-out overflow-hidden"
                style={{
                  maxHeight: hasMessages ? 0 : '200px',
                  opacity: hasMessages ? 0 : 1,
                  marginTop: hasMessages ? 0 : '1.5rem',
                }}
              >
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                  {[
                    t('chat.suggestion1'),
                    t('chat.suggestion2'),
                    t('chat.suggestion3'),
                    t('chat.suggestion4'),
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(suggestion)}
                      className="p-3 rounded-lg border text-left text-sm transition-colors hover:border-opacity-80"
                      style={{
                        borderColor: 'var(--border-default)',
                        color: 'var(--text-primary)',
                        backgroundColor: 'var(--bg-card)',
                      }}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Messages Area - Only visible when has messages */}
          <div
            className="flex-1 overflow-y-auto transition-all duration-300 ease-in-out"
            style={{
              opacity: hasMessages ? 1 : 0,
              pointerEvents: hasMessages ? 'auto' : 'none',
            }}
          >
            <div className="max-w-3xl mx-auto">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div
                  className="flex gap-4 p-4 rounded-lg my-2"
                  style={{ backgroundColor: 'var(--bg-secondary, #f3f4f6)' }}
                >
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
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
                  <div className="flex items-center gap-1">
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: 'var(--text-tertiary)', animationDelay: '0ms' }}
                    />
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: 'var(--text-tertiary)', animationDelay: '150ms' }}
                    />
                    <div
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: 'var(--text-tertiary)', animationDelay: '300ms' }}
                    />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
