# AI RAG ChatBot Documentation

This document provides a comprehensive overview of the AI RAG (Retrieval-Augmented Generation) ChatBot, covering both the backend and frontend architectures, setup instructions, and feature details.

---

## 1. System Overview

The AI RAG ChatBot is a full-stack application designed to let users upload various document types and ask questions about their content. The system extracts text from the uploaded documents, stores it in chunks, and uses an Ollama LLM to answer questions strictly based on the extracted context.

- **Backend**: Python (Flask)
- **Frontend**: JavaScript (React + Vite)
- **AI Model**: Ollama (via `ollama` SDK)

---

## 2. Backend Architecture

The backend is built with **Flask** and handles document uploading, text extraction, local storage, and communication with the Ollama model.

### 2.1 Supported File Types & Extraction
The backend supports the following file formats, utilizing specific libraries for text extraction:
- **PDF (`.pdf`)**: Extracted using `pypdf`. If the PDF is scanned or has very little text, it falls back to OCR using `pdf2image` and `pytesseract`.
- **Word (`.doc`, `.docx`)**: Extracted using `python-docx`.
- **Excel (`.xls`, `.xlsx`)**: Extracted using `openpyxl`.
- **CSV (`.csv`)**: Extracted using the built-in `csv` module.
- **PowerPoint (`.ppt`, `.pptx`)**: Extracted using `python-pptx`.

### 2.2 Storage & Retrieval (RAG)
- **Storage**: Extracted text is saved locally in a JSON file (`document_store.json`) acting as a simple document store. Physical files are also temporarily stored in the `uploads/` directory.
- **Chunking**: When a user asks a question, the text of all uploaded documents is split into manageable chunks (overlapping to retain context).
- **Retrieval**: A lightweight keyword-matching algorithm scores chunks based on the question's non-stop words. The top relevant chunks are injected into the LLM prompt as context.

### 2.3 API Endpoints
- `GET /health`: Health check endpoint.
- `POST /upload`: Accepts a `multipart/form-data` file upload, extracts text, and stores it.
- `GET /documents`: Returns a list of all currently uploaded document filenames.
- `DELETE /documents/<filename>`: Deletes a document from the store and removes the physical file.
- `POST /chat`: Accepts a JSON payload `{"question": "..."}`, retrieves relevant document chunks, and queries Ollama for an answer.

### 2.4 Setup & Execution
**Prerequisites**: Python 3.8+ and Tesseract OCR installed on the system (if OCR is needed).

1. Navigate to the backend directory: `cd backend`
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Environment Variables: Create a `.env` file in the backend directory with:
   ```env
   OLLAMA_BASE_URL="http://localhost:11434"
   OLLAMA_MODEL="llama3.2:1b"
   TESSERACT_PATH=path_to_tesseract_executable
   ```
5. Run the server:
   ```bash
   python app.py
   ```
   *The server runs by default on `http://0.0.0.0:8001`.*

---

## 3. Frontend Architecture

The frontend is a modern single-page application (SPA) built with **React** and bundled using **Vite**.

### 3.1 Key Components
- **Sidebar (`Sidebar.jsx`)**: Displays the list of uploaded documents, allows deleting documents, toggling between Light/Dark themes, and includes a drag-and-drop file upload zone.
- **Upload Page (`UploadPage.jsx`)**: The primary interface for dragging and dropping files or browsing to upload. It handles upload states (loading spinners) and displays success or error messages.
- **Chat Page (`ChatPage.jsx`)**: The main interface where users interact with the AI. It maintains the chat history.
- **Source Panel (`SourcePanel.jsx`)**: A side panel that shows exactly which document chunks were retrieved to answer the user's most recent question, providing transparency and citations.
- **API Service (`api.js`)**: An Axios-based service wrapper for communicating with the Flask backend.

### 3.2 Setup & Execution
**Prerequisites**: Node.js and npm installed.

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *The application typically runs on `http://localhost:5173`.*

---

## 4. Key Features & Workflows

1. **Upload Workflow**: User drops a file -> Frontend sends FormData to `/upload` -> Backend identifies extension -> Extracts text -> Saves to `document_store.json` -> Returns chunk count.
2. **Chat Workflow**: User asks question -> Frontend sends to `/chat` -> Backend chunks all stored text -> Scores chunks against question -> Prompts Ollama with top chunks -> Returns answer and source metadata -> Frontend displays chat bubble and populates the Source Panel.
3. **Theming**: The frontend supports a persistent dark and light mode toggle.
4. **Configuration**: The backend is configured to point to a local Ollama instance but can be easily changed via `.env` variables to any remote Ollama server.

---

## 5. Troubleshooting & Tips

### 5.1 Out of Memory Errors (Ollama)
If your system has limited RAM and you encounter errors like `failed to allocate CPU buffer of size...` or `failed to initialize the context` when asking a question, this means Ollama cannot load the selected model into your computer's memory.
- **Fix 1 (Use a smaller model)**: In this project, we explicitly chose `llama3.2:1b` as the default because it's highly optimized for low-memory environments (only requires ~1.3GB of RAM).
- **Fix 2 (Lower Context Window)**: The `num_ctx` is deliberately set to `512` in `backend/chat.py` to prevent Ollama from reserving massive memory buffers for conversation history. If you still encounter memory issues, consider lowering it to `256`.

### 5.2 Missing Model (Status Code 404)
If you get a `model not found` error, it means you haven't downloaded the configured model yet.
- Open your command prompt and run: `ollama pull llama3.2:1b` (or whichever model you configured in `.env`). 
- Wait for the download to reach 100% before testing the application.
