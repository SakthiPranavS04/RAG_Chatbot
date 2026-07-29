import React from 'react';

const Sidebar = ({ activeTab, setActiveTab, documents }) => {
  return (
    <aside className="sidebar">
      <h2>AI RAG ChatBot</h2>
      
      <div className="nav-buttons">
        <button 
          className={`nav-btn ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload Document
        </button>
        <button 
          className={`nav-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat interface
        </button>
      </div>

      <div className="doc-list">
        <h3>Uploaded Documents</h3>
        {documents.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No documents uploaded yet.</p>
        ) : (
          documents.map((doc, idx) => (
            <div key={idx} className="doc-item">
              {doc}
            </div>
          ))
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
