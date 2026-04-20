import React, { useState, useRef, useEffect, useCallback } from 'react';
import './ChatPanel.css';

const API_GATEWAY_URL = 'http://localhost:8006/ask';

interface Source {
  source?: string;
  page?: number;
  // legacy shape from retrieval path
  metadata?: { page?: number; source?: string; chunk_id?: string };
  score?: number;
  text?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

const SUGGESTIONS = [
  'What are the key findings in this document?',
  'Summarize the main topics covered.',
  'What are the conclusions or recommendations?',
  'List the most important data points.',
];

function formatTime(d: Date): string {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function genId(): string {
  return Math.random().toString(36).slice(2, 10);
}

const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, loading, scrollToBottom]);

  const autoResize = () => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`;
  };

  const sendMessage = useCallback(async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: genId(),
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setLoading(true);

    try {
      const res = await fetch(API_GATEWAY_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed }),
      });

      if (!res.ok) throw new Error(`Gateway responded with ${res.status}`);
      const data = await res.json();

      const aiMsg: Message = {
        id: genId(),
        role: 'assistant',
        content: data.answer ?? 'No answer was returned from the model.',
        sources: data.sources ?? [],
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err: unknown) {
      const text = err instanceof Error ? err.message : 'An unexpected error occurred.';
      setMessages(prev => [
        ...prev,
        {
          id: genId(),
          role: 'assistant',
          content: `⚠️ Error connecting to the RAG pipeline:\n${text}\n\nMake sure the Docker services are running.`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="chat-title gradient-text">Ask Your Documents</span>
          <span className="chat-subtitle">Multimodal RAG — text &amp; vision retrieval</span>
        </div>
        {messages.length > 0 && (
          <button className="clear-btn" onClick={() => setMessages([])} id="clear-chat-btn">
            🗑 Clear chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="messages-area" id="messages-area">
        {messages.length === 0 && !loading ? (
          <div className="empty-state">
            <div className="empty-orb">🧠</div>
            <h2 className="empty-title gradient-text">Ready to answer</h2>
            <p className="empty-desc">
              Upload a PDF in the sidebar and start asking questions. The RAG pipeline will retrieve relevant text and images to power each answer.
            </p>
            <div className="suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => sendMessage(s)}
                  id={`suggestion-${i}`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map(msg => (
              <div key={msg.id} className={`message-row ${msg.role}`} id={`msg-${msg.id}`}>
                <div className={`avatar ${msg.role === 'user' ? 'user-avatar' : 'ai-avatar'}`}>
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className={`bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}`}>
                    {msg.content}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources-wrap">
                      <span className="sources-label">Sources</span>
                      <div className="sources-list">
                        {msg.sources.map((src, i) => {
                          // Generation service returns {source, page}
                          // Retrieval service returns {metadata: {source, page}}
                          const page = src.page ?? src.metadata?.page;
                          const sourceName = src.source ?? src.metadata?.source ?? `chunk-${i + 1}`;
                          const label = page !== undefined ? `${sourceName} · p.${page}` : sourceName;
                          return (
                            <span key={i} className="source-tag">{label}</span>
                          );
                        })}
                      </div>
                    </div>
                  )}
                  <span className="msg-time">{formatTime(msg.timestamp)}</span>
                </div>
              </div>
            ))}
            {loading && (
              <div className="typing-row">
                <div className="avatar ai-avatar">🤖</div>
                <div className="typing-bubble">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Bar */}
      <div className="input-bar">
        <div className="input-wrap">
          <textarea
            ref={textareaRef}
            id="chat-input"
            className="chat-textarea"
            rows={1}
            placeholder="Ask anything about your documents…"
            value={input}
            onChange={e => { setInput(e.target.value); autoResize(); }}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            id="send-btn"
            className="send-btn"
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            title="Send (Enter)"
          >
            ➤
          </button>
        </div>
        <p className="input-hint">Press Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
};

export default ChatPanel;
