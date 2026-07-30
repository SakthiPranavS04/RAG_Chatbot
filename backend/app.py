import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from document_service import process_and_store_document
from chat import chat_with_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"detail": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"detail": "No selected file"}), 400
        
    allowed_extensions = {"pdf", "csv", "xls", "xlsx", "ppt", "pptx", "doc", "docx"}
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        return jsonify({"detail": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"}), 400
        
    try:
        content = file.read()
        chunks_processed = process_and_store_document(content, file.filename)
        return jsonify({
            "filename": file.filename,
            "message": "File processed and stored successfully",
            "chunks_processed": chunks_processed
        })
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({"detail": str(e)}), 500

@app.route("/documents", methods=["GET"])
def get_documents():
    from document_service import get_all_documents
    return jsonify(get_all_documents())

@app.route("/documents/<filename>", methods=["DELETE"])
def remove_document(filename):
    from document_service import delete_document
    success = delete_document(filename)
    if success:
        return jsonify({"message": f"Document {filename} deleted successfully"})
    return jsonify({"detail": f"Document {filename} not found"}), 404

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data:
        return jsonify({"detail": "No JSON payload provided"}), 400
    question = data.get("question", "")
    try:
        response = chat_with_documents(question)
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({"detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True, use_reloader=False)
