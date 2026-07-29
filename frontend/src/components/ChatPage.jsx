import React, { useState, useRef, useEffect } from 'react';
import { chatWithDocuments } from '../services/api';
import SourcePanel from './SourcePanel';

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hello! I am ready to answer questions about your uploaded documents.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentSources, setCurrentSources] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const userMsg = inputValue.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInputValue('');
    setIsTyping(true);
    
    try {
      const response = await chatWithDocuments(userMsg);
      setMessages(prev => [...prev, { role: 'bot', text: response.answer }]);
      setCurrentSources(response.sources || []);
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
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div>{msg.text}</div>
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
        
        <div className="input-area">
          <input 
            type="text" 
            placeholder="Ask a question about your documents..." 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
          />
          <button onClick={handleSend} disabled={isTyping || !inputValue.trim()}>
            ➤
          </button>
        </div>
      </div>
      
      <SourcePanel sources={currentSources} />
    </div>
  );
};

export default ChatPage;
