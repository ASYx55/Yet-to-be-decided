"""
Embedding Utilities Module.

Handles conversion of raw text into dense vector embeddings
using a shared SentenceTransformer model.

Copyright (c) 2026 suy0x1
"""

from .model import get_model

model = get_model()


def embed_text(text: str):
    """
    Convert a single text string into a semantic vector embedding.

    Embeddings are numerical vector representations of text that
    preserve semantic meaning. Similar sentences produce vectors
    that are close together in vector space.

    Args:
        text (str):
            The input sentence or paragraph to embed.

    Returns:
        list[float]:
            A dense vector embedding represented as a Python list.

    Example:
        >>> embed_text("Student struggles with recursion")
        [0.123, -0.991, ...]

    Typical Use Cases:
        - Semantic search
        - Retrieval-Augmented Generation (RAG)
        - Recommendation systems
        - Memory retrieval systems
        - Similarity comparison

    Notes:
        - Internally uses SentenceTransformer.encode().
        - Output dimension depends on the model.
        - Returned as `.tolist()` for ChromaDB compatibility.
    """
    return model.encode(text).tolist()


def embed_batch(docs: list[str]):
    """
    Embed multiple documents at once.

    This function converts a list of text documents into
    semantic vector embeddings suitable for vector databases
    like ChromaDB.

    Args:
        docs (list[str]):
            A list of text documents or sentences.

    Returns:
        list[list[float]]:
            A list containing one embedding vector per document.

    Example:
        >>> docs = [
        ...     "Student struggles with recursion",
        ...     "Student likes visual explanations"
        ... ]
        >>> embeddings = embed_batch(docs)

    Returns Structure:
        [
            [0.12, -0.44, ...],
            [0.91, 0.22, ...]
        ]

    Notes:
        - Each embedding preserves semantic meaning.
        - Useful before inserting documents into ChromaDB.
        - Internally calls `embed_text()` for each document.
    """
    return [embed_text(doc) for doc in docs]
