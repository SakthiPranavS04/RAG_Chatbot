import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { chatWithDocuments } from '../services/api';
import SourcePanel from './SourcePanel';

const ChatPage = ({ theme }) => {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am ready to answer questions about your uploaded documents.' }
  ]);
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

  const handleNewChat = () => {
    setMessages([
      { role: 'bot', text: 'Hello! I am ready to answer questions about your uploaded documents.' }
    ]);
    setCurrentSources({ question: null, sources: [] });
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const userMsg = inputValue.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInputValue('');
    setIsTyping(true);
    
    try {
      const response = await chatWithDocuments(userMsg);
      setMessages(prev => [...prev, { role: 'bot', text: response.answer }]);
      setCurrentSources({ question: userMsg, sources: response.sources || [] });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Sorry, I encountered an error while retrieving the answer.';
      setMessages(prev => [...prev, { 
        role: 'bot', 
        text: errorMsg, 
        error: true 
      }]);
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

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div style={{ padding: '10px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'flex-end' }}>
          <button 
            className="new-chat-btn"
            onClick={handleNewChat}
          >
            + New Chat
          </button>
        </div>
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', fontSize: '0.8rem', opacity: 0.8, fontWeight: '600' }}>
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
              {msg.role === 'bot' ? (
                <div className="markdown-content">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
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
      
      <SourcePanel sources={currentSources} theme={theme} />
    </div>
  );
};

export default ChatPage;
