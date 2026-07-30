import React from 'react';

const SourcePanel = ({ sources, theme }) => {
  const questionText = sources?.question || null;
  const sourcesList = sources?.sources || [];

  const textColor = theme === 'dark' ? '#ffffff' : '#000000';
  const mutedColor = theme === 'dark' ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.6)';

  return (
    <div className="source-panel">
      <h3 style={{ color: textColor }}>Sources</h3>
      {questionText && (
        <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)', borderRadius: '6px', borderLeft: '3px solid var(--primary-color)' }}>
          <span style={{ fontSize: '0.8rem', color: mutedColor, display: 'block', marginBottom: '4px' }}>For question:</span>
          <span style={{ fontSize: '0.9rem', fontStyle: 'italic', color: textColor }}>"{questionText}"</span>
        </div>
      )}
      {sourcesList.length === 0 ? (
        <p style={{ color: mutedColor, fontSize: '0.9rem' }}>
          No sources to display. Ask a question to see retrieved document chunks.
        </p>
      ) : (
        sourcesList.map((source, idx) => (
          <div key={idx} className="source-card">
            <div className="filename" style={{ color: textColor }}>{source.filename}</div>
            <div className="meta" style={{ color: mutedColor }}>Page/Row: {source.page}</div>
            <div className="meta" style={{ color: mutedColor }}>Chunk ID: {source.chunk_id.substring(0, 15)}...</div>
          </div>
        ))
      )}
    </div>
  );
};

export default SourcePanel;
