import streamlit as st
import os
import subprocess
import sys
from utils import generate_answer, DATA_DIR, CHROMA_DB_DIR

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
st.set_page_config(page_title="Local RAG Chatbot", layout="centered")

st.title("Local RAG Chatbot")
st.write("Welcome! This chatbot uses your local PDFs to answer questions.")

# -------------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------------
with st.sidebar:
    st.header("Settings & Data")
    # File Uploader
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload files to add to the knowledge base", 
        type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Save Uploaded Files & Rebuild"):
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            
            for file in uploaded_files:
                file_path = os.path.join(DATA_DIR, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            st.success(f"Saved {len(uploaded_files)} files!")
            
            with st.spinner("Rebuilding Knowledge Base... This may take a moment."):
                try:
                    subprocess.run([sys.executable, "ingest.py"], capture_output=True, text=True, check=True)
                    st.success("Knowledge Base successfully rebuilt!")
                except subprocess.CalledProcessError as e:
                    st.error(f"Failed to rebuild knowledge base: {e.stderr}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    
    # Button to trigger the backend ingest.py script manually
    if st.button("Rebuild Knowledge Base Manually"):
        with st.spinner("Rebuilding Knowledge Base... This may take a moment."):
            try:
                subprocess.run([sys.executable, "ingest.py"], capture_output=True, text=True, check=True)
                st.success("Knowledge Base successfully rebuilt!")
            except subprocess.CalledProcessError as e:
                st.error(f"Failed to rebuild knowledge base: {e.stderr}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
    st.markdown("---")
    
    # Show files currently loaded
    st.subheader("Loaded Files")
    if os.path.exists(DATA_DIR):
        supported_extensions = ('.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg')
        data_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(supported_extensions)]
        if data_files:
            for f in data_files:
                col1, col2 = st.columns([0.85, 0.15], vertical_alignment="center")
                with col1:
                    st.markdown(f"📄 {f}")
                with col2:
                    if st.button("", icon=":material/delete:", type="tertiary", key=f"del_{f}", help=f"Delete {f}"):
                        try:
                            os.remove(os.path.join(DATA_DIR, f))
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting file: {e}")
        else:
            st.write("No supported files found in the 'data' folder.")
    else:
        st.write(f"The '{DATA_DIR}' folder does not exist.")
        
    st.markdown("---")
    
    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------------------
# Chat History Management
# -------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Re-display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------------------
# User Input & Chat Logic
# -------------------------------------------------------------
if prompt := st.chat_input("Ask a question about your documents..."):
    
    # Save user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user input
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and searching documents..."):
            try:
                # Check if the Chroma DB directory exists before querying
                if not os.path.exists(CHROMA_DB_DIR):
                    response = "No knowledge base found. Please click Rebuild Knowledge Base in the sidebar."
                else:
                    # Execute LCEL RAG logic
                    answer, sources = generate_answer(prompt)
                    
                    if sources:
                        source_text = "\n\n**Sources:**\n"
                        for s in sources:
                            source_text += f"- {os.path.basename(s)}\n"
                        response = answer + source_text
                    else:
                        response = answer
                    
                st.markdown(response)
                
                # Save assistant response
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
