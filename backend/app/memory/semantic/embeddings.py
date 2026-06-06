"""
Embedding utilities for semantic memory systems.

This module provides helper functions for converting raw text into
dense vector embeddings using a shared SentenceTransformer model.
Separate formatting strategies are used for retrieval queries and
stored memory passages to improve embedding alignment and retrieval
quality.

Embedding Types:
    - query embeddings
    - memory/passage embeddings
    - batch memory embeddings

The module normalizes all embeddings to support cosine similarity
search through vector distance operations.

Copyright (c) 2026 suy0x1
"""

from .model import get_model

model = get_model()


def embed_query(text: str) -> list[float]:
    """
    Generate a normalized embedding for a retrieval query.

    Query embeddings are prefixed using the ``query:`` format to
    improve semantic alignment with passage embeddings during
    retrieval tasks.

    Args:
        text:
            Natural language retrieval query.

    Returns:
        Normalized dense vector embedding representing the query.
    """

    formatted = f"query: {text}"

    return model.encode(
        formatted,
        normalize_embeddings=True,
    ).tolist()

def embed_batch(docs: list[str]) -> list[list[float]]:
    """
    Generate normalized embeddings for multiple memory passages.

    Batch embedding improves throughput when indexing or updating
    large groups of semantic memories.

    Args:
        docs:
            List of memory or passage texts to embed.

    Returns:
        List of normalized dense vector embeddings corresponding
        to the provided documents.
    """

    formatted_docs = [
        f"passage: {doc}"
        for doc in docs
    ]

    return model.encode(
        formatted_docs,
        normalize_embeddings=True,
    ).tolist()
