import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import UploadPage from './components/UploadPage';
import ChatPage from './components/ChatPage';
import './styles/global.css';
import { getDocuments, deleteDocument } from './services/api';

function App() {
  const [documents, setDocuments] = useState([]);
  const [theme, setTheme] = useState('dark');
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const addDocument = (filename) => {
    if (!documents.includes(filename)) {
      setDocuments([...documents, filename]);
    }
  };

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const docs = await getDocuments();
        setDocuments(docs);
      } catch (err) {
        console.error("Failed to fetch documents", err);
      }
    };
    fetchDocs();

    const savedChats = localStorage.getItem('chatbot_chats');
    if (savedChats) {
      try {
        const parsed = JSON.parse(savedChats);
        setChats(parsed);
        if (parsed.length > 0) {
          setActiveChatId(parsed[0].id);
        } else {
          createNewChat();
        }
      } catch (e) {
        createNewChat();
      }
    } else {
      createNewChat();
    }
  }, []);

  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem('chatbot_chats', JSON.stringify(chats));
    } else {
      localStorage.removeItem('chatbot_chats');
    }
  }, [chats]);

  const createNewChat = () => {
    // Prevent creating multiple empty new chats
    if (chats.length > 0 && chats[0].messages.length === 1 && chats[0].title === 'New Chat') {
      setActiveChatId(chats[0].id);
      return;
    }

    const newChat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [{ role: 'bot', text: 'Hello! I am ready to answer questions about your uploaded documents.' }],
      createdAt: new Date().toISOString()
    };
    setChats(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  const updateChat = (id, newMessages, title) => {
    setChats(prev => prev.map(c => {
      if (c.id === id) {
        return { ...c, messages: newMessages, title: title || c.title };
      }
      return c;
    }));
  };

  const deleteChat = (id) => {
    setChats(prev => {
      const updated = prev.filter(c => c.id !== id);
      if (activeChatId === id) {
        if (updated.length > 0) {
          setActiveChatId(updated[0].id);
        } else {
          setTimeout(createNewChat, 0);
        }
      }
      return updated;
    });
  };

  const handleDeleteDocument = async (filename) => {
    try {
      await deleteDocument(filename);
      setDocuments(documents.filter(doc => doc !== filename));
    } catch (err) {
      console.error("Failed to delete document", err);
    }
  };

  const activeChat = chats.find(c => c.id === activeChatId) || null;

  return (
    <div className="app-container" data-theme={theme}>
      <Sidebar 
        documents={documents} 
        onDeleteDocument={handleDeleteDocument}
        onUploadSuccess={addDocument}
        theme={theme}
        toggleTheme={toggleTheme}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onDeleteChat={deleteChat}
        onNewChat={createNewChat}
      />
      <main className="main-content">
        <ChatPage 
          theme={theme} 
          activeChat={activeChat} 
          updateChat={updateChat} 
          onNewChat={createNewChat}
          chats={chats}
          onSelectChat={setActiveChatId}
          onDeleteChat={deleteChat}
        />
      </main>
    </div>
  );
}

export default App;
