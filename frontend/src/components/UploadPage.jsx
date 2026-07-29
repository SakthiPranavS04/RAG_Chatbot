import React, { useState, useRef } from 'react';
import { uploadFile } from '../services/api';

const UploadPage = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

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

  const handleFileSelect = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFile(e.target.files[0]);
    }
  };

  const processFile = async (file) => {
    setUploading(true);
    setMessage('');
    setError('');
    
    try {
      const response = await uploadFile(file);
      setMessage(`Success! Processed ${response.chunks_processed} chunks from ${response.filename}`);
      onUploadSuccess(response.filename);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during upload.');
    } finally {
      setUploading(false);
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="upload-page">
      <div 
        className={`upload-area ${isDragging ? 'dragover' : ''}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <div className="upload-icon">Upload</div>
        <div className="upload-text">Drag and drop your file here</div>
        <div className="upload-subtext">or click to browse</div>
        <div className="upload-subtext" style={{ marginTop: '10px' }}>
          Supported: PDF, CSV, Excel, PPT (Max 50MB)
        </div>
        
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileSelect}
          accept=".pdf,.csv,.xls,.xlsx,.ppt,.pptx"
        />
      </div>

      {uploading && (
        <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div className="spinner"></div>
          <p>Processing document, performing OCR if needed...</p>
        </div>
      )}

      {message && <p style={{ marginTop: '20px', color: 'var(--success-color)' }}>{message}</p>}
      {error && <p style={{ marginTop: '20px', color: 'var(--error-color)' }}>{error}</p>}
    </div>
  );
};

export default UploadPage;
