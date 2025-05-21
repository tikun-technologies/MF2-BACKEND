from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from azure.storage.blob import BlobServiceClient
import os
import uuid
from datetime import datetime
import tempfile
import threading
import json
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'pptx'}

# Database setup
mongo_client = MongoClient('mongodb+srv://dlovej009:Dheeraj2006@cluster0.dnu8vna.mongodb.net/?retryWrites=true&w=majority')
db = mongo_client['llm_chat']

# Azure Blob Storage setup
blob_service = BlobServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=printxd;AccountKey=CaL/3SmhK8iKVM02i/cIN1VgE3058lyxRnCxeRd2J1k/9Ay6I67GC2CMnW//lJhNl+71WwxYXHnC+AStkbW1Jg==;EndpointSuffix=core.windows.net"
)

# Create containers if they don't exist
for container_name in ['rnd', 'marketing']:
    try:
        blob_service.create_container(container_name)
    except Exception as e:
        if "ContainerAlreadyExists" not in str(e):
            raise e

# Initialize Ollama components
ollama_embeddings = OllamaEmbeddings(model="llama3.1")
llm = Ollama(model="llama3.1")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_document(file_path, content_type):
    try:
        if content_type == 'application/pdf':
            loader = PyPDFLoader(file_path)
        elif content_type == 'text/plain':
            loader = TextLoader(file_path)
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            loader = Docx2txtLoader(file_path)
        else:
            return None
        
        pages = loader.load()
        texts = text_splitter.split_documents(pages)
        return texts
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        return None

def create_vector_store(texts, chat_id, bucket):
    try:
        # Create persistent Chroma DB for each chat+bucket combination
        persist_directory = f"./chroma_db/{chat_id}_{bucket}"
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=ollama_embeddings,
            persist_directory=persist_directory
        )
        vectordb.persist()
        return vectordb
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

def generate_ai_response(chat_id, bucket, question):
    try:
        # Load the appropriate vector store
        persist_directory = f"./chroma_db/{chat_id}_{bucket}"
        vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=ollama_embeddings
        )
        
        # Set up RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever()
        )
        
        # Generate response
        response = qa_chain.run(question)
        return response
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return f"Error generating response: {str(e)}"

@app.route('/api/chats', methods=['POST', 'OPTIONS'])
def create_chat():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    chat_id = str(uuid.uuid4())
    
    chat_data = {
        "chat_id": chat_id,
        "user_id": user_id,
        "title": data.get('title', 'New Chat'),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "rnd_documents": [],
        "marketing_documents": []
    }
    
    db.chats.insert_one(chat_data)
    return jsonify({
        "success": True,
        "chat_id": chat_id,
        "title": chat_data["title"],
        "created_at": chat_data["created_at"]
    }), 201

@app.route('/api/chats/<chat_id>/upload', methods=['POST', 'OPTIONS'])
def upload_file(chat_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if 'file' not in request.files or 'bucket' not in request.form:
        return jsonify({"error": "Missing file or bucket parameter"}), 400
    
    bucket = request.form['bucket']
    if bucket not in ['rnd', 'marketing']:
        return jsonify({"error": "Invalid bucket. Must be 'rnd' or 'marketing'"}), 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400
    
    try:
        uploaded_files = []
        
        for file in files:
            if not allowed_file(file.filename):
                continue
            
            # Generate unique filename
            filename = f"{chat_id}-{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            
            # Save to temp file for processing
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)
            
            # Process document and create vector store
            texts = process_document(temp_path, file.content_type)
            if texts:
                create_vector_store(texts, chat_id, bucket)
            
            # Upload to Azure Blob Storage
            container_client = blob_service.get_container_client(bucket)
            blob_client = container_client.get_blob_client(filename)
            with open(temp_path, 'rb') as f:
                blob_client.upload_blob(f)
            
            # Store document metadata
            doc_id = str(uuid.uuid4())
            document_data = {
                "doc_id": doc_id,
                "chat_id": chat_id,
                "user_id": request.form.get('user_id', 'default_user'),
                "filename": file.filename,
                "bucket": bucket,
                "blob_url": blob_client.url,
                "content_type": file.content_type,
                "size": file.content_length,
                "created_at": datetime.utcnow()
            }
            
            db.documents.insert_one(document_data)
            uploaded_files.append(document_data)
            
            # Add document reference to chat
            db.chats.update_one(
                {"chat_id": chat_id},
                {"$push": {f"{bucket}_documents": doc_id}, "$set": {"updated_at": datetime.utcnow()}}
            )
            
            # Clean up temp file
            os.remove(temp_path)
            os.rmdir(temp_dir)
        
        # Generate system message about the upload
        message_id = str(uuid.uuid4())
        message = {
            "message_id": message_id,
            "chat_id": chat_id,
            "user_id": "system",
            "text": f"Uploaded {len(uploaded_files)} file(s) to {bucket}",
            "is_ai": False,
            "bucket": bucket,
            "document_refs": [f["doc_id"] for f in uploaded_files],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.messages.insert_one(message)
        
        # Generate AI response about the uploaded documents
        ai_message_id = str(uuid.uuid4())
        question = f"Please analyze the uploaded {bucket} documents and provide a summary"
        ai_response = generate_ai_response(chat_id, bucket, question)
        
        ai_message = {
            "message_id": ai_message_id,
            "chat_id": chat_id,
            "user_id": "ai",
            "text": ai_response,
            "is_ai": True,
            "bucket": bucket,
            "document_refs": [f["doc_id"] for f in uploaded_files],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.messages.insert_one(ai_message)
        
        return jsonify({
            "success": True,
            "uploaded_files": [{
                "doc_id": f["doc_id"],
                "filename": f["filename"],
                "bucket": f["bucket"],
                "url": f["blob_url"],
                "size": f["size"]
            } for f in uploaded_files],
            "ai_response": ai_response
        }), 201
        
    except Exception as e:
        return jsonify({"error": "File upload failed", "details": str(e)}), 500

@app.route('/api/chats/<chat_id>/ask', methods=['POST', 'OPTIONS'])
def ask_question(chat_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    question = data.get('question', '')
    bucket = data.get('bucket', None)
    user_id = data.get('user_id', 'default_user')
    
    if not question:
        return jsonify({"error": "Question cannot be empty"}), 400
    
    try:
        # Save user question as a message
        message_id = str(uuid.uuid4())
        message = {
            "message_id": message_id,
            "chat_id": chat_id,
            "user_id": user_id,
            "text": question,
            "is_ai": False,
            "bucket": bucket,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.messages.insert_one(message)
        
        # Generate AI response
        ai_response = generate_ai_response(chat_id, bucket, question)
        
        # Save AI response
        ai_message_id = str(uuid.uuid4())
        ai_message = {
            "message_id": ai_message_id,
            "chat_id": chat_id,
            "user_id": "ai",
            "text": ai_response,
            "is_ai": True,
            "bucket": bucket,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.messages.insert_one(ai_message)
        
        # Update chat's updated_at
        db.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": ai_response,
            "message_id": message_id,
            "ai_message_id": ai_message_id
        })
        
    except Exception as e:
        return jsonify({"error": "Failed to process question", "details": str(e)}), 500

@app.route('/api/chats/user/<user_id>', methods=['GET', 'OPTIONS'])
def get_user_chats(user_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        chats = list(db.chats.find(
            {"user_id": user_id},
            {"_id": 0, "chat_id": 1, "title": 1, "updated_at": 1, 
             "rnd_documents": 1, "marketing_documents": 1}
        ).sort("updated_at", -1).limit(50))
        
        return jsonify({
            "success": True,
            "chats": [{
                "chat_id": c["chat_id"],
                "title": c["title"],
                "updated_at": c["updated_at"],
                "has_rnd_documents": len(c.get("rnd_documents", [])) > 0,
                "has_marketing_documents": len(c.get("marketing_documents", [])) > 0
            } for c in chats]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chats/<chat_id>/messages', methods=['GET', 'OPTIONS'])
def get_chat_messages(chat_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        messages = list(db.messages.find(
            {"chat_id": chat_id},
            {"_id": 0, "message_id": 1, "text": 1, "is_ai": 1, 
             "created_at": 1, "document_refs": 1, "bucket": 1}
        ).sort("created_at", 1).limit(100))
        
        # Get document details for messages that have references
        doc_refs = set()
        for msg in messages:
            doc_refs.update(msg.get('document_refs', []))
        
        documents = {}
        if doc_refs:
            docs = db.documents.find({"doc_id": {"$in": list(doc_refs)}})
            for doc in docs:
                documents[doc["doc_id"]] = {
                    "filename": doc["filename"],
                    "url": doc.get("blob_url", ""),
                    "content_type": doc.get("content_type", ""),
                    "bucket": doc.get("bucket", "")
                }
        
        return jsonify({
            "success": True,
            "messages": messages,
            "documents": documents
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _build_cors_preflight_response():
    response = jsonify({"message": "Preflight request received"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

if __name__ == '__main__':
    # Create chroma_db directory if it doesn't exist
    os.makedirs("./chroma_db", exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=8000)