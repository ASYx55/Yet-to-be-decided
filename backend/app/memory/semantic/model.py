"""
Shared embedding model initialization utilities.

This module provides a globally initialized SentenceTransformer
instance used throughout the semantic memory system for generating
dense vector embeddings.

A singleton-style model instance is used to avoid repeated model
loading overhead and to improve runtime efficiency during retrieval
and indexing operations.

Model:
    - intfloat/e5-base-v2
    - optimized for semantic retrieval tasks
    - supports query/passage embedding alignment

Copyright (c) 2026 suy0x1
"""

from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("intfloat/e5-base-v2")


def get_model() -> SentenceTransformer:
    """
    Return the shared SentenceTransformer embedding model instance.

    The embedding model is initialized once at module load time and
    reused across the application to reduce startup latency and
    memory overhead.

    Returns:
        Shared SentenceTransformer model instance used for semantic
        embedding generation.

    Notes:
        - Uses the ``e5-base-v2`` embedding model.
        - Designed for query/passage retrieval workflows.
        - Supports normalized semantic vector embeddings.
        - Reusing a single model instance is significantly more
          efficient than repeatedly loading the model.
    """

    return _model
