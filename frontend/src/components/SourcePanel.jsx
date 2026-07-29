import React from 'react';

const SourcePanel = ({ sources }) => {
  return (
    <div className="source-panel">
      <h3>Sources</h3>
      {sources.length === 0 ? (
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          No sources to display. Ask a question to see retrieved document chunks.
        </p>
      ) : (
        sources.map((source, idx) => (
          <div key={idx} className="source-card">
            <div className="filename">📄 {source.filename}</div>
            <div className="meta">Page/Row: {source.page}</div>
            <div className="meta">Chunk ID: {source.chunk_id.substring(0, 15)}...</div>
          </div>
        ))
      )}
    </div>
  );
};

export default SourcePanel;
