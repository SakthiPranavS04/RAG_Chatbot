import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadPage from './components/UploadPage';
import ChatPage from './components/ChatPage';
import './styles/global.css';
import { getDocuments, deleteDocument } from './services/api';

function App() {
  const [documents, setDocuments] = useState([]);
  const [theme, setTheme] = useState('dark');

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const addDocument = (filename) => {
    if (!documents.includes(filename)) {
      setDocuments([...documents, filename]);
    }
  };

  React.useEffect(() => {
    const fetchDocs = async () => {
      try {
        const docs = await getDocuments();
        setDocuments(docs);
      } catch (err) {
        console.error("Failed to fetch documents", err);
      }
    };
    fetchDocs();
  }, []);

  const handleDeleteDocument = async (filename) => {
    try {
      await deleteDocument(filename);
      setDocuments(documents.filter(doc => doc !== filename));
    } catch (err) {
      console.error("Failed to delete document", err);
    }
  };

  return (
    <div className="app-container" data-theme={theme}>
      <Sidebar 
        documents={documents} 
        onDeleteDocument={handleDeleteDocument}
        onUploadSuccess={addDocument}
        theme={theme}
        toggleTheme={toggleTheme}
      />
      <main className="main-content">
        <ChatPage theme={theme} />
      </main>
    </div>
  );
}

export default App;
