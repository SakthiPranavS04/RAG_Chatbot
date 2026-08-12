import React, { useRef, useState } from 'react';
import { uploadFile } from '../services/api';

const Sidebar = ({ documents, onDeleteDocument, onUploadSuccess, theme, toggleTheme, chats, activeChatId, onSelectChat, onDeleteChat, onNewChat }) => {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await processFile(e.dataTransfer.files[0]);
    }
  };

  const processFile = async (file) => {
    setIsUploading(true);
    try {
      const response = await uploadFile(file);
      onUploadSuccess(response.filename);
    } catch (err) {
      console.error("Upload failed", err);
      alert(err.response?.data?.detail || 'An error occurred during upload.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleFileSelect = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFile(e.target.files[0]);
    }
  };

  return (
    <aside className="sidebar">
      <h2>AI RAG ChatBot</h2>
      
      <div 
        className="upload-section" 
        style={{ 
          margin: '20px 0',
          border: isDragging 
            ? `2px dashed ${theme === 'dark' ? '#ffffff' : '#000000'}` 
            : `2px dashed ${theme === 'dark' ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)'}`,
          borderRadius: '8px',
          padding: '20px 10px',
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragging ? (theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)') : 'transparent',
          transition: 'all 0.2s ease',
          opacity: isUploading ? 0.5 : 1,
          pointerEvents: isUploading ? 'none' : 'auto'
        }}
        onClick={() => fileInputRef.current.click()}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div style={{ color: theme === 'dark' ? '#ffffff' : '#000000', fontSize: '0.9rem', fontWeight: '500' }}>
          {isUploading ? 'Uploading...' : 'Upload file here or drag the files'}
        </div>
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileSelect}
          accept=".pdf,.csv,.xls,.xlsx,.ppt,.pptx,.doc,.docx"
          style={{ display: 'none' }}
        />
      </div>



      <div className="doc-list">
        <h3>Uploaded Documents</h3>
        {documents.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No documents uploaded yet.</p>
        ) : (
          documents.map((doc, idx) => (
            <div key={idx} className="doc-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="doc-name">{doc}</span>
              <button 
                className="delete-btn"
                onClick={() => onDeleteDocument(doc)} 
                title="Delete document"
                style={{ 
                  backgroundColor: 'transparent', 
                  color: '#dc3545', 
                  border: '1px solid #dc3545', 
                  borderRadius: '4px', 
                  padding: '4px 8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                </svg>
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
