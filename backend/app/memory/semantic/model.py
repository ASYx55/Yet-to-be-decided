"""
Embedding Model Module.

Provides a singleton SentenceTransformer model instance used
for generating semantic embeddings across the system.

Copyright (c) 2026 suy0x1
"""

from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_model():
    """
    Return the globally initialized SentenceTransformer model.

    This function ensures the embedding model is loaded only once
    during application startup. Reusing a single model instance is
    significantly faster and more memory-efficient than loading
    the model repeatedly inside multiple functions.

    Returns:
        SentenceTransformer:
            A preloaded sentence-transformer embedding model.

    Example:
        >>> from model import get_model
        >>> model = get_model()
        >>> emb = model.encode("hello world")

    Notes:
        - Uses the `all-MiniLM-L6-v2` embedding model.
        - Produces dense semantic vector embeddings.
        - Embedding dimension for this model is 384.
    """
    return _model