import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { chatWithDocuments } from '../services/api';
import SourcePanel from './SourcePanel';

const ChatPage = ({ theme, activeChat, updateChat, onNewChat, chats, onSelectChat, onDeleteChat }) => {
  const messages = activeChat?.messages || [];
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentSources, setCurrentSources] = useState({ question: null, sources: [] });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    // Reset sources when switching chats
    setCurrentSources({ question: null, sources: [] });
  }, [activeChat?.id]);

  const handleSend = async () => {
    if (!inputValue.trim() || !activeChat) return;
    
    const userMsg = inputValue.trim();
    
    // Update title if it's the first user message
    let newTitle = activeChat.title;
    if (messages.length === 1 && activeChat.title === 'New Chat') {
      newTitle = userMsg.substring(0, 30) + (userMsg.length > 30 ? '...' : '');
    }

    const newMessages = [...messages, { role: 'user', text: userMsg }];
    updateChat(activeChat.id, newMessages, newTitle);
    
    setInputValue('');
    setIsTyping(true);
    
    try {
      const response = await chatWithDocuments(userMsg);
      updateChat(activeChat.id, [...newMessages, { role: 'bot', text: response.answer }], newTitle);
      setCurrentSources({ question: userMsg, sources: response.sources || [] });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Sorry, I encountered an error while retrieving the answer.';
      updateChat(activeChat.id, [...newMessages, { 
        role: 'bot', 
        text: errorMsg, 
        error: true 
      }], newTitle);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleBookmark = (idx) => {
    if (!activeChat) return;
    const updatedMessages = messages.map((msg, i) => {
      if (i === idx) {
        return { ...msg, bookmarked: !msg.bookmarked };
      }
      return msg;
    });
    updateChat(activeChat.id, updatedMessages);
  };

  const handleExport = () => {
    if (!activeChat) return;
    
    let exportText = `Chat Export - ${activeChat.title}\nDate: ${new Date(activeChat.createdAt).toLocaleString()}\n\n`;
    messages.forEach(msg => {
      exportText += `[${msg.role.toUpperCase()}]\n${msg.text}\n\n`;
    });
    
    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_export_${activeChat.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!activeChat) {
    return <div className="chat-page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>No active chat. Create a new chat to start.</div>;
  }

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div style={{ padding: '10px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: theme === 'dark' ? '#fff' : '#000' }}>
            {activeChat.title}
          </h3>
          <button 
            className="export-btn"
            onClick={handleExport}
            style={{
              background: 'transparent',
              color: 'var(--primary-color)',
              border: '1px solid var(--primary-color)',
              borderRadius: '4px',
              padding: '4px 12px',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            Export Chat
          </button>
        </div>
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', opacity: 0.8, fontWeight: '600' }}>
                  {msg.role === 'user' ? (
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0"/>
                        <path fillRule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1"/>
                      </svg>
                      <span>You</span>
                    </>
                  ) : (
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.889a28.94 28.94 0 0 1 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.933.933 0 0 1-.765.935c-.845.147-2.34.346-4.235.346-1.895 0-3.39-.2-4.235-.346A.933.933 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/>
                        <path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/>
                      </svg>
                      <span>AI Assistant</span>
                    </>
                  )}
                </div>
                {msg.role === 'bot' && idx > 0 && (
                  <button 
                    onClick={() => toggleBookmark(idx)}
                    title={msg.bookmarked ? "Remove Bookmark" : "Bookmark this answer"}
                    style={{ 
                      background: 'transparent', 
                      border: 'none', 
                      cursor: 'pointer',
                      color: msg.bookmarked ? 'var(--primary-color)' : 'var(--text-muted)'
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z"/>
                    </svg>
                  </button>
                )}
              </div>
              {msg.role === 'bot' ? (
                <div className="markdown-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                </div>
              ) : (
                <div>{msg.text}</div>
              )}
              {msg.error && <div className="message-error" style={{marginTop: '8px', color: '#ff4d4f'}}>Request Failed</div>}
            </div>
          ))}
          {isTyping && (
            <div className="message bot">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="predefined-questions" style={{ display: 'flex', gap: '10px', padding: '10px 20px', flexWrap: 'wrap', borderTop: '1px solid var(--border-color)' }}>
          {['What is the main topic of the documents?', 'Can you summarize the key points?', 'What are the conclusions?', 'List all mentioned dates and events.'].map((q, idx) => (
            <button 
              key={idx}
              onClick={() => setInputValue(q)}
              style={{
                background: theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                color: theme === 'dark' ? '#ffffff' : '#000000',
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                padding: '6px 12px',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              {q}
            </button>
          ))}
        </div>
        
        <div className="input-area">
          <input 
            type="text" 
            placeholder="Ask a question about your documents..." 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
          />
          <button onClick={handleSend} disabled={isTyping || !inputValue.trim()} className="send-btn">
            Send
          </button>
        </div>
      </div>
      <SourcePanel 
        sources={currentSources} 
        theme={theme} 
        chats={chats}
        activeChatId={activeChat?.id}
        onSelectChat={onSelectChat}
        onDeleteChat={onDeleteChat}
        onNewChat={onNewChat}
      />
    </div>
  );
};

export default ChatPage;
