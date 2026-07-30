import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { chatWithDocuments } from '../services/api';
import SourcePanel from './SourcePanel';

const ChatPage = () => {
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
      setMessages(prev => [...prev, { 
        role: 'bot', 
        text: 'Sorry, I encountered an error while retrieving the answer.', 
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
              {msg.role === 'bot' ? (
                <div className="markdown-content">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              ) : (
                <div>{msg.text}</div>
              )}
              {msg.error && <div className="message-error">Error connecting to server.</div>}
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
                background: 'var(--bg-secondary)',
                color: 'var(--text-primary)',
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
      
      <SourcePanel sources={currentSources} />
    </div>
  );
};

export default ChatPage;
