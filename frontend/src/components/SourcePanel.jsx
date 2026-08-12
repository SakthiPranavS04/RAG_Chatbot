import React from 'react';

const SourcePanel = ({ sources, theme, chats, activeChatId, onSelectChat, onDeleteChat, onNewChat }) => {
  const questionText = sources?.question || null;
  const sourcesList = sources?.sources || [];

  const textColor = theme === 'dark' ? '#ffffff' : '#000000';
  const mutedColor = theme === 'dark' ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)';

  return (
    <div className="source-panel" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* Chat History Section */}
      <div className="chat-history-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0, color: textColor }}>Chat History</h3>
          <button 
            onClick={onNewChat}
            style={{ 
              background: 'var(--primary-color)', 
              color: 'white', 
              border: 'none', 
              borderRadius: '6px', 
              padding: '6px 12px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: '500',
              transition: 'background var(--trans-fast)'
            }}
          >
            + New
          </button>
        </div>
        
        {(!chats || chats.length === 0) ? (
          <p style={{ color: mutedColor, fontSize: '0.85rem' }}>No past chats.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
            {chats.map((chat) => (
              <div 
                key={chat.id} 
                className="chat-item" 
                onClick={() => onSelectChat(chat.id)}
                style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  backgroundColor: activeChatId === chat.id 
                    ? (theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)') 
                    : 'transparent',
                  border: activeChatId === chat.id 
                    ? '1px solid var(--primary-color)' 
                    : '1px solid transparent',
                  transition: 'all 0.2s ease'
                }}
              >
                <span style={{ 
                  color: activeChatId === chat.id ? textColor : mutedColor, 
                  fontSize: '0.9rem',
                  fontWeight: activeChatId === chat.id ? '500' : '400',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  maxWidth: '160px'
                }}>
                  {chat.title}
                </span>
                <button 
                  className="delete-btn"
                  onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }} 
                  title="Delete chat"
                  style={{ 
                    backgroundColor: 'transparent', 
                    color: '#ef4444', 
                    border: 'none', 
                    cursor: 'pointer',
                    padding: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '4px',
                    transition: 'background 0.2s'
                  }}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sources Section */}
      <div className="sources-section">
        <h3 style={{ color: textColor, marginBottom: '15px' }}>Sources</h3>
        {questionText && (
          <div style={{ marginBottom: '15px', padding: '12px', backgroundColor: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)', borderRadius: '8px', borderLeft: '4px solid var(--primary-color)' }}>
            <span style={{ fontSize: '0.8rem', color: mutedColor, display: 'block', marginBottom: '6px', fontWeight: '500' }}>For question:</span>
            <span style={{ fontSize: '0.9rem', fontStyle: 'italic', color: textColor }}>"{questionText}"</span>
          </div>
        )}
        {sourcesList.length === 0 ? (
          <p style={{ color: mutedColor, fontSize: '0.9rem', lineHeight: '1.5' }}>
            No sources to display. Ask a question to see retrieved document chunks.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {sourcesList.map((source, idx) => (
              <div key={idx} className="source-card">
                <div className="filename" style={{ color: textColor }}>{source.filename}</div>
                <div className="meta" style={{ color: mutedColor }}>Page/Row: {source.page}</div>
                <div className="meta" style={{ color: mutedColor }}>Chunk ID: {source.chunk_id.substring(0, 15)}...</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SourcePanel;
