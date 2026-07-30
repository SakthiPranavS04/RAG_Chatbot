import React from 'react';

const SourcePanel = ({ sources }) => {
  const questionText = sources?.question || null;
  const sourcesList = sources?.sources || [];

  return (
    <div className="source-panel">
      <h3>Sources</h3>
      {questionText && (
        <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', borderLeft: '3px solid var(--primary-color)' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>For question:</span>
          <span style={{ fontSize: '0.9rem', fontStyle: 'italic' }}>"{questionText}"</span>
        </div>
      )}
      {sourcesList.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          No sources to display. Ask a question to see retrieved document chunks.
        </p>
      ) : (
        sourcesList.map((source, idx) => (
          <div key={idx} className="source-card">
            <div className="filename">{source.filename}</div>
            <div className="meta">Page/Row: {source.page}</div>
            <div className="meta">Chunk ID: {source.chunk_id.substring(0, 15)}...</div>
          </div>
        ))
      )}
    </div>
  );
};

export default SourcePanel;
