import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadPage from './components/UploadPage';
import ChatPage from './components/ChatPage';
import './styles/global.css';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [documents, setDocuments] = useState([]);

  const addDocument = (filename) => {
    if (!documents.includes(filename)) {
      setDocuments([...documents, filename]);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        documents={documents} 
      />
      <main className="main-content">
        {activeTab === 'upload' ? (
          <UploadPage onUploadSuccess={addDocument} />
        ) : (
          <ChatPage />
        )}
      </main>
    </div>
  );
}

export default App;
