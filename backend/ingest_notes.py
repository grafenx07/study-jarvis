"""
Note Ingestion Script
Handles uploading and processing of study notes (PDF, DOCX, TXT)
"""
import os
import sys
import uuid
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
import docx
from dotenv import load_dotenv
import pinecone_client

load_dotenv()

# Lazy-load embedding model
_embed_model = None

def get_embed_model():
    """Get or initialize the embedding model"""
    global _embed_model
    if _embed_model is None:
        print("Loading embedding model...")
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded!")
    return _embed_model

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into chunks with overlap

    Args:
        text: Full text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        # Don't create tiny chunks at the end
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())

        start += (chunk_size - overlap)

    return chunks

def read_pdf(file_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return ""

def read_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"❌ Error reading DOCX: {e}")
        return ""

def read_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading TXT: {e}")
        return ""

def extract_text(file_path):
    """Extract text based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return read_pdf(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext == '.txt':
        return read_txt(file_path)
    else:
        print(f"❌ Unsupported file type: {ext}")
        return ""

def ingest_file(file_path, subject=None, chapter=None):
    """
    Main ingestion function

    Args:
        file_path: Path to the file to ingest
        subject: Subject/course name (optional metadata)
        chapter: Chapter/topic name (optional metadata)

    Returns:
        Number of chunks ingested
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return 0

    print(f"\n📄 Processing: {os.path.basename(file_path)}")

    # Extract text
    print("📖 Extracting text...")
    text = extract_text(file_path)

    if not text.strip():
        print("❌ No text extracted from file")
        return 0

    print(f"✅ Extracted {len(text)} characters")

    # Chunk text
    print("✂️  Chunking text...")
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    print(f"✅ Created {len(chunks)} chunks")

    # Create embeddings
    print("🧮 Creating embeddings...")
    embed_model = get_embed_model()
    embeddings = embed_model.encode(chunks, show_progress_bar=True)

    # Prepare vectors for Pinecone
    print("📦 Preparing vectors for upload...")
    vectors = []
    filename = os.path.basename(file_path)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vector_id = f"{uuid.uuid4()}"
        metadata = {
            "text": chunk,
            "source": filename,
            "chunk_index": i,
        }

        # Add optional metadata
        if subject:
            metadata["subject"] = subject
        if chapter:
            metadata["chapter"] = chapter

        vectors.append((vector_id, embedding.tolist(), metadata))

    # Upload to Pinecone
    print("☁️  Uploading to Pinecone...")
    success = pinecone_client.upsert_vectors(vectors)

    if success:
        print(f"✅ Successfully ingested {len(chunks)} chunks from {filename}")
        return len(chunks)
    else:
        print("❌ Failed to upload to Pinecone")
        return 0

def ingest_directory(directory_path, subject=None):
    """Ingest all supported files in a directory"""
    if not os.path.exists(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        return

    total_chunks = 0
    supported_extensions = ['.pdf', '.docx', '.txt']

    print(f"\n📁 Processing directory: {directory_path}")

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        if os.path.isfile(file_path) and ext in supported_extensions:
            chunks = ingest_file(file_path, subject=subject)
            total_chunks += chunks

    print(f"\n🎉 Total chunks ingested: {total_chunks}")

if __name__ == "__main__":
    # Initialize Pinecone
    print("🔧 Initializing Pinecone...")
    pinecone_client.init_index()

    # Check command line arguments
    if len(sys.argv) < 2:
        print("""
Usage:
    python ingest_notes.py <file_or_directory> [subject] [chapter]

Examples:
    python ingest_notes.py notes.pdf "Data Structures" "Chapter 1"
    python ingest_notes.py my_notes/ "Operating Systems"
    python ingest_notes.py lecture.txt
        """)
        sys.exit(1)

    path = sys.argv[1]
    subject = sys.argv[2] if len(sys.argv) > 2 else None
    chapter = sys.argv[3] if len(sys.argv) > 3 else None

    if os.path.isfile(path):
        ingest_file(path, subject, chapter)
    elif os.path.isdir(path):
        ingest_directory(path, subject)
    else:
        print(f"❌ Invalid path: {path}")
