"""
Semantic Retrieval Module.

Implements high-level search functionality over vector embeddings
stored in ChromaDB.

Copyright (c) 2026 suy0x1
"""

from .embeddings import embed_text
from .chroma_store import query_collection

def search(collection, query_text: str, k=3):
    """
    Perform end-to-end semantic search using raw text input.

    This function:
        1. Converts the query text into an embedding
        2. Searches the vector database
        3. Returns nearest semantic matches

    Args:
        collection:
            ChromaDB collection object.

        query_text (str):
            Natural language query.

        k (int, optional):
            Number of nearest results to retrieve.
            Defaults to 3.

    Returns:
        dict:
            ChromaDB search results.

    Example:
        >>> results = search(
        ...     collection,
        ...     "I don't understand recursive calls",
        ...     k=2
        ... )

    Typical Use Cases:
        - Memory retrieval
        - Semantic search
        - RAG pipelines
        - Conversational AI context retrieval

    Notes:
        - Uses semantic similarity, not keyword matching.
        - Similar meaning can match even without exact words.
    """
    query_embedding = embed_text(query_text)
    return query_collection(collection, query_embedding, k)