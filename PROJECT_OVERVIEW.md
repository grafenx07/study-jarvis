# Study Jarvis - Project Overview

## 📖 What is Study Jarvis?

Study Jarvis is an AI-powered study assistant that helps students learn more effectively by:
- Understanding your personal study notes
- Answering questions based on your materials
- Generating summaries, quizzes, and flashcards
- Using completely local, self-hosted technology (no cloud APIs for LLM)

## 🏗️ Technical Architecture

### Technology Stack

**Backend:**
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.10+**: Programming language
- **Sentence Transformers**: For creating text embeddings (all-MiniLM-L6-v2)
- **PyPDF2**: PDF text extraction
- **python-docx**: Word document processing

**Vector Database:**
- **Pinecone**: Cloud-based vector database for semantic search

**LLM (Large Language Model):**
- **Ollama**: Local LLM runtime
- **LLaMA 3**: 8B parameter open-source model (or Mistral 7B)

**Frontend:**
- **HTML5 + CSS3 + Vanilla JavaScript**: Simple, no-framework approach
- **Responsive Design**: Works on desktop and mobile

### How It Works (RAG Architecture)

```
1. Document Ingestion:
   User uploads notes → Split into chunks → Create embeddings → Store in Pinecone

2. Query Processing:
   User asks question → Create query embedding → Find similar chunks in Pinecone

3. Response Generation:
   Retrieve relevant chunks → Build prompt with context → Send to LLM → Return answer
```

## 📁 File Structure Explained

```
personal-jarvis/
│
├── backend/                    # Backend API
│   ├── app.py                 # Main FastAPI application with all endpoints
│   ├── ingest_notes.py        # Script to process and upload notes
│   ├── pinecone_client.py     # Pinecone vector database wrapper
│   ├── llm_client.py          # Ollama LLM communication
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment variable template
│   └── .env                   # Your actual config (create this)
│
├── frontend/                   # Frontend interface
│   └── index.html             # Single-page chat application
│
├── models/                     # (Optional) For local model storage
│
├── sample_notes.txt           # Example study notes
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick setup guide
├── setup.ps1                  # Automated setup script
├── .gitignore                 # Git ignore rules
└── package.json               # Project metadata
```

## 🔑 Key Components

### 1. Backend API (`app.py`)

**Endpoints:**
- `GET /`: Health check
- `GET /status`: Check system status (LLM, DB)
- `POST /upload`: Upload study notes (PDF/DOCX/TXT)
- `POST /chat`: Ask questions about notes
- `POST /quiz`: Generate quiz questions
- `GET /history/{session_id}`: View conversation history

**Features:**
- CORS enabled for frontend access
- Multi-format file support
- Session-based conversation tracking
- Multiple interaction modes

### 2. Pinecone Client (`pinecone_client.py`)

**Functions:**
- `init_index()`: Create or connect to Pinecone index
- `upsert_vectors()`: Upload embeddings to database
- `query_vectors()`: Semantic search for relevant content
- `delete_all()`: Clear database (use carefully!)

**Configuration:**
- Index dimension: 384 (matches all-MiniLM-L6-v2)
- Metric: Cosine similarity
- Cloud: AWS (configurable)

### 3. LLM Client (`llm_client.py`)

**Functions:**
- `query_llm()`: Send prompts to Ollama
- `build_study_prompt()`: Create structured prompts for different modes
- `check_ollama_status()`: Verify LLM availability

**Prompt Templates:**
- Answer mode: Context-based Q&A
- Summarize mode: Concise summaries
- Quiz mode: Multiple-choice questions
- Flashcard mode: Question-answer pairs

### 4. Note Ingestion (`ingest_notes.py`)

**Features:**
- Multi-format support (PDF, DOCX, TXT)
- Intelligent text chunking (500 chars with 50 char overlap)
- Automatic embedding generation
- Metadata tagging (subject, chapter, source)
- Batch processing for directories

### 5. Frontend (`index.html`)

**Components:**
- Sidebar: Mode selector, file upload, status indicators
- Chat area: Message history with context display
- Input area: Text input with send button
- Real-time status monitoring

**Modes:**
- 💬 Answer Questions: Standard Q&A
- 📝 Summarize Notes: Topic summarization
- 📋 Generate Quiz: Create practice questions
- 🎴 Create Flashcards: Study card generation

## 🔄 Data Flow

### Upload Flow:
```
1. User selects file in UI
2. Frontend sends to /upload endpoint
3. Backend extracts text (PDF/DOCX/TXT)
4. Text split into 500-char chunks with overlap
5. Each chunk converted to 384-dim embedding
6. Embeddings + metadata uploaded to Pinecone
7. Success message returned to user
```

### Chat Flow:
```
1. User types question in chat
2. Frontend sends to /chat endpoint with mode
3. Backend creates embedding of question
4. Pinecone searches for top-5 similar chunks
5. Relevant chunks used as context
6. Structured prompt built based on mode
7. Prompt sent to Ollama (LLaMA 3)
8. LLM generates contextual response
9. Response + sources returned to UI
10. Conversation saved in session history
```

## 🎯 Use Cases

### 1. Exam Preparation
- Upload all lecture notes
- Ask: "Summarize Chapter 5 key points"
- Generate practice quizzes
- Create flashcards for memorization

### 2. Concept Clarification
- Upload textbook chapters
- Ask: "Explain recursion in simple terms"
- Get answers from your own materials

### 3. Quick Revision
- Upload semester notes
- Ask: "What are the main differences between X and Y?"
- Get concise, sourced answers

### 4. Self-Assessment
- Upload course materials
- Generate quizzes: "10 questions on databases"
- Test your knowledge

## 🔧 Configuration Options

### Environment Variables (`.env`)

```bash
# Pinecone (Required)
PINECONE_API_KEY=xxxxx          # Get from pinecone.io
PINECONE_CLOUD=aws              # aws, gcp, or azure
PINECONE_REGION=us-east-1       # Your region

# Ollama (Optional - defaults shown)
OLLAMA_URL=http://localhost:11434
LLM_MODEL=llama3                # or mistral, llama2, etc.
```

### Customizable Parameters

**In `ingest_notes.py`:**
- `chunk_size`: Default 500 characters
- `overlap`: Default 50 characters

**In `app.py`:**
- `top_k`: Number of relevant chunks (default 5)
- `max_tokens`: LLM response length (default 512)
- `temperature`: LLM creativity (default 0.7)

**In `pinecone_client.py`:**
- `DIMENSION`: Embedding dimension (384 for MiniLM)
- `INDEX_NAME`: Database name (study-jarvis)

## 🚀 Performance Considerations

### Embedding Model
- **Current**: all-MiniLM-L6-v2 (384 dims, fast, good quality)
- **Upgrade**: all-mpnet-base-v2 (768 dims, better quality, slower)

### LLM Model
- **Fast**: LLaMA 3 8B (~4 GB, 20-30 tokens/sec)
- **Better**: LLaMA 3 70B (~40 GB, slower, more accurate)
- **Alternative**: Mistral 7B (fast, good quality)

### Chunk Strategy
- Smaller chunks (300-400): More precise retrieval
- Larger chunks (600-800): More context per match
- Overlap: Prevents context splitting across chunks

## 🔒 Security & Privacy

### Data Privacy
- **LLM**: Runs completely locally (no data sent to cloud)
- **Embeddings**: Generated locally
- **Notes**: Stored in Pinecone (cloud vector DB)

### Production Considerations
- Add authentication (JWT tokens)
- Use HTTPS for API
- Rate limiting on endpoints
- Input validation and sanitization
- API key rotation

## 🐛 Common Issues & Solutions

### Issue: "Cannot connect to Ollama"
**Solution:**
```powershell
ollama serve
```

### Issue: "Pinecone authentication failed"
**Solution:** Check API key in `.env`, verify Pinecone account is active

### Issue: "No relevant context found"
**Solution:** Upload more notes, check if embeddings were created, verify Pinecone has vectors

### Issue: "Slow LLM responses"
**Solution:** Try smaller model (mistral 7B), reduce max_tokens, upgrade hardware

## 📈 Future Roadmap

### Phase 1 (Current)
- [x] Basic RAG implementation
- [x] Multi-format note support
- [x] Quiz and flashcard generation
- [x] Web interface

### Phase 2 (Enhancements)
- [ ] User authentication
- [ ] SQLite for persistent conversations
- [ ] Better UI with React
- [ ] Streaming responses (SSE)

### Phase 3 (Advanced)
- [ ] Multi-user support
- [ ] Chrome extension
- [ ] Voice input/output
- [ ] Spaced repetition system
- [ ] Mind map generation
- [ ] Mobile app

### Phase 4 (Scale)
- [ ] Replace Pinecone with ChromaDB (fully local)
- [ ] Fine-tuned models for education
- [ ] Analytics dashboard
- [ ] Collaborative study groups

## 📚 Learning Resources

### Understanding RAG
- RAG = Retrieval Augmented Generation
- Combines retrieval (search) + generation (LLM)
- Reduces hallucinations by providing context

### Vector Embeddings
- Transform text into numerical vectors
- Similar meanings = similar vectors
- Enables semantic search (not just keywords)

### Ollama
- Run LLMs locally without complex setup
- API compatible with OpenAI format
- Supports many open-source models

## 🤝 Contributing

Want to improve Study Jarvis? Ideas:
- Add support for images/diagrams
- Implement spaced repetition algorithm
- Create browser extension
- Add real-time collaboration
- Improve prompt engineering
- Add more LLM models support

## 📄 License

This project is for educational purposes. Please respect:
- LLaMA 3 license (Meta)
- Mistral license
- Pinecone terms of service

---

**Built for students, by students** 🎓

Questions? Check README.md or QUICKSTART.md for detailed setup instructions.
