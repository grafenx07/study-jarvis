"""
Pinecone Vector Database Client
Handles initialization, indexing, and querying of document embeddings
"""
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "study-jarvis"
DIMENSION = 384  # all-MiniLM-L6-v2 embedding dimension

def init_index():
    """Initialize Pinecone index if it doesn't exist"""
    try:
        # Check if index exists
        existing_indexes = [index.name for index in pc.list_indexes()]

        if INDEX_NAME not in existing_indexes:
            print(f"Creating new index: {INDEX_NAME}")
            pc.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=os.getenv("PINECONE_CLOUD", "aws"),
                    region=os.getenv("PINECONE_REGION", "us-east-1")
                )
            )
            print(f"✅ Index '{INDEX_NAME}' created successfully!")
        else:
            print(f"✅ Index '{INDEX_NAME}' already exists")

        return pc.Index(INDEX_NAME)
    except Exception as e:
        print(f"❌ Error initializing Pinecone index: {e}")
        raise

def get_index():
    """Get the Pinecone index instance"""
    try:
        return pc.Index(INDEX_NAME)
    except Exception as e:
        print(f"❌ Error getting index: {e}")
        return init_index()

def upsert_vectors(vectors):
    """
    Upsert vectors to Pinecone
    vectors: list of tuples (id, embedding, metadata)
    """
    try:
        index = get_index()
        index.upsert(vectors=vectors)
        print(f"✅ Upserted {len(vectors)} vectors to Pinecone")
        return True
    except Exception as e:
        print(f"❌ Error upserting vectors: {e}")
        return False

def query_vectors(query_embedding, top_k=5, filter=None):
    """
    Query Pinecone for similar vectors
    Returns: list of matches with metadata
    """
    try:
        index = get_index()
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        return results.get('matches', [])
    except Exception as e:
        print(f"❌ Error querying vectors: {e}")
        return []

def get_document_stats():
    """Get statistics about stored documents by scanning metadata"""
    try:
        index = get_index()
        stats = index.describe_index_stats()

        documents = {}

        # Use query with zero vector to sample documents
        # Fetch larger sample to get all unique sources
        try:
            sample_results = index.query(
                vector=[0.0] * DIMENSION,
                top_k=10000,  # Increased to get more results
                include_metadata=True
            )

            for match in sample_results.get('matches', []):
                if match.get('metadata'):
                    source = match['metadata'].get('source', 'Unknown')

                    if source not in documents:
                        documents[source] = {
                            'name': source,
                            'chunks': 0,
                            'upload_time': match['metadata'].get('upload_time', 'Unknown'),
                            'subject': match['metadata'].get('subject', 'General')
                        }
                    documents[source]['chunks'] += 1
        except Exception as e:
            print(f"Warning: Could not fetch all documents: {e}")

        return {
            'total_vectors': stats.get('total_vector_count', 0),
            'documents': sorted(list(documents.values()), key=lambda x: x.get('upload_time', ''), reverse=True)
        }
    except Exception as e:
        print(f"❌ Error getting document stats: {e}")
        return {
            'total_vectors': 0,
            'documents': []
        }

def delete_document(source_name):
    """
    Delete all vectors for a specific document

    Args:
        source_name: The filename/source to delete

    Returns:
        dict with success status and count of deleted vectors
    """
    try:
        index = get_index()

        # Use the filter to delete vectors with matching source
        delete_response = index.delete(filter={"source": {"$eq": source_name}})

        print(f"✅ Deleted document: {source_name}")
        return {
            'success': True,
            'message': f'Successfully deleted {source_name}',
            'source': source_name
        }
    except Exception as e:
        print(f"❌ Error deleting document {source_name}: {e}")
        return {
            'success': False,
            'message': f'Error deleting document: {str(e)}',
            'source': source_name
        }

def delete_all():
    """Delete all vectors from the index (use with caution!)"""
    try:
        index = get_index()
        index.delete(delete_all=True)
        print("✅ Deleted all vectors from index")
        return True
    except Exception as e:
        print(f"❌ Error deleting vectors: {e}")
        return False

if __name__ == "__main__":
    # Test initialization
    print("Testing Pinecone connection...")
    init_index()
    print("Pinecone setup complete!")
