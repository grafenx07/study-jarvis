"""
Study Jarvis - FastAPI Backend
Main API for the AI Study Assistant
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import tempfile
from datetime import datetime
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

import pinecone_client
import llm_client
from ingest_notes import extract_text, chunk_text, get_embed_model

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Study Jarvis API",
    description="AI-powered study assistant with RAG capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get embedding model (lazy-loaded)
embed_model = None

def get_or_init_model():
    global embed_model
    if embed_model is None:
        print("🔧 Loading embedding model...")
        embed_model = get_embed_model()
        print("✅ Embedding model loaded!")
    return embed_model

# Initialize Pinecone
print("🔧 Initializing Pinecone...")
pinecone_client.init_index()
print("✅ Pinecone initialized!")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    mode: Optional[str] = "answer"  # answer, summarize, quiz, flashcard
    top_k: Optional[int] = 10  # Increased from 5 to get more context

class ChatResponse(BaseModel):
    answer: str
    context_used: List[str]
    sources: List[str]
    timestamp: str

class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks_created: int
    message: str

class StatusResponse(BaseModel):
    status: str
    pinecone_status: str
    llm_status: str
    models_available: List[str]

# In-memory conversation storage (use database in production)
conversations = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Study Jarvis API is running! 🤖",
        "version": "1.0.0",
        "endpoints": {
            "/status": "Check system status",
            "/upload": "Upload notes (PDF, DOCX, TXT)",
            "/chat": "Ask questions about your notes",
            "/history": "Get conversation history"
        }
    }

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Check status of all services"""
    llm_status = llm_client.check_ollama_status()

    return StatusResponse(
        status="online",
        pinecone_status="connected",
        llm_status=llm_status["status"],
        models_available=llm_status.get("models", [])
    )

@app.get("/documents")
async def get_documents():
    """Get list of uploaded documents and their statistics"""
    try:
        stats = pinecone_client.get_document_stats()
        return {
            "status": "success",
            "total_vectors": stats['total_vectors'],
            "documents": stats['documents'],
            "document_count": len(stats['documents'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")

@app.delete("/documents/{source_name}")
async def delete_document(source_name: str):
    """Delete a specific document by source name"""
    try:
        # URL decode the source name
        from urllib.parse import unquote
        decoded_source = unquote(source_name)

        result = pinecone_client.delete_document(decoded_source)

        if result['success']:
            return {
                "status": "success",
                "message": result['message'],
                "source": result['source']
            }
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.post("/upload", response_model=UploadResponse)
async def upload_notes(
    file: UploadFile = File(...),
    subject: Optional[str] = Form(None),
    chapter: Optional[str] = Form(None)
):
    """
    Upload and process study notes
    Supports: PDF, DOCX, TXT files
    """
    try:
        # Check file extension
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ['.pdf', '.docx', '.txt']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Please upload PDF, DOCX, or TXT files."
            )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Extract text
        text = extract_text(tmp_path)

        if not text.strip():
            os.unlink(tmp_path)
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file"
            )

        # Chunk text
        chunks = chunk_text(text, chunk_size=500, overlap=50)

        # Create embeddings
        model = get_or_init_model()
        embeddings = model.encode(chunks)

        # Prepare vectors for Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = str(uuid.uuid4())
            metadata = {
                "text": chunk,
                "source": filename,
                "chunk_index": i,
                "upload_time": datetime.now().isoformat()
            }

            if subject:
                metadata["subject"] = subject
            if chapter:
                metadata["chapter"] = chapter

            vectors.append((vector_id, embedding.tolist(), metadata))

        # Upload to Pinecone
        success = pinecone_client.upsert_vectors(vectors)

        # Cleanup
        os.unlink(tmp_path)

        if success:
            return UploadResponse(
                status="success",
                filename=filename,
                chunks_created=len(chunks),
                message=f"Successfully processed {filename} into {len(chunks)} chunks"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload to vector database"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with your notes using RAG

    Modes:
    - answer: Answer questions based on notes
    - summarize: Summarize notes on a topic
    - quiz: Generate quiz questions
    - flashcard: Create flashcards
    """
    try:
        # Create embedding for query
        model = get_or_init_model()
        query_embedding = model.encode([request.message])[0].tolist()

        # Retrieve relevant chunks from Pinecone
        matches = pinecone_client.query_vectors(
            query_embedding=query_embedding,
            top_k=request.top_k
        )

        # Extract context and sources
        context_chunks = []
        sources = []

        for match in matches:
            if match.get('metadata'):
                text = match['metadata'].get('text', '')
                source = match['metadata'].get('source', 'Unknown')

                # Prefix each chunk with its source so the LLM can cite and quote from it
                labeled_chunk = f"[source={source}]\n{text}"
                context_chunks.append(labeled_chunk)
                if source not in sources:
                    sources.append(source)

        # Build prompt based on mode
        prompt = llm_client.build_study_prompt(
            context_chunks=context_chunks,
            user_question=request.message,
            mode=request.mode
        )

        # Query LLM
        answer = llm_client.query_llm(prompt)

        # Store conversation
        if request.session_id not in conversations:
            conversations[request.session_id] = []

        conversations[request.session_id].append({
            "timestamp": datetime.now().isoformat(),
            "question": request.message,
            "answer": answer,
            "mode": request.mode,
            "sources": sources
        })

        return ChatResponse(
            answer=answer,
            context_used=context_chunks[:3],  # Return top 3 contexts
            sources=sources,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversations:
        return {"session_id": session_id, "messages": []}

    return {
        "session_id": session_id,
        "messages": conversations[session_id]
    }

@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversations:
        del conversations[session_id]
        return {"message": f"History cleared for session {session_id}"}
    return {"message": "Session not found"}

@app.post("/quiz")
async def generate_quiz(
    topic: str = Form(...),
    num_questions: int = Form(5),
    subject: Optional[str] = Form(None)
):
    """Generate a quiz based on notes"""
    try:
        # Create embedding for topic
        model = get_or_init_model()
        query_embedding = model.encode([topic])[0].tolist()

        # Build filter if subject provided
        filter_dict = {"subject": subject} if subject else None

        # Retrieve relevant chunks
        matches = pinecone_client.query_vectors(
            query_embedding=query_embedding,
            top_k=10,
            filter=filter_dict
        )

        context_chunks = [m['metadata'].get('text', '') for m in matches if m.get('metadata')]

        # Generate quiz
        prompt = llm_client.build_study_prompt(
            context_chunks=context_chunks,
            user_question=str(num_questions),
            mode="quiz"
        )

        quiz = llm_client.query_llm(prompt, max_tokens=1024)

        return {
            "topic": topic,
            "num_questions": num_questions,
            "quiz": quiz
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Study Jarvis Backend...")
    print("📍 Server: http://127.0.0.1:8000")
    print("📖 API Docs: http://127.0.0.1:8000/docs\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
