"""
Persistent ChromaDB vector storage utilities.

This module provides the low-level persistence and retrieval layer
for semantic memory storage. It manages ChromaDB collections,
document insertion, vector similarity queries, and metadata-aware
filtering operations used throughout the adaptive tutoring system.

Features:
    - persistent collection management
    - semantic vector retrieval
    - metadata filtering
    - document and embedding storage
    - disk-backed persistence

Copyright (c) 2026 suy0x1
"""

import uuid
import chromadb


_client = chromadb.PersistentClient(
    path="./database/chroma"
)


def get_client():
    """
    Return the shared persistent ChromaDB client instance.

    The client is initialized once at module load time and reused
    across the application to minimize initialization overhead and
    maintain consistent access to the persistent vector store.

    Returns:
        Shared persistent ChromaDB client instance.
    """

    return _client


def create_collection(name: str = "memory"):
    """
    Create or retrieve a persistent ChromaDB collection.

    Collections store semantic documents, embeddings, metadata,
    and unique identifiers used during retrieval operations.

    Args:
        name:
            Name of the collection to create or retrieve.

    Returns:
        Persistent ChromaDB collection instance.

    Notes:
        - Existing collections are automatically reused.
        - Collections are persisted on disk.
        - Collection creation is idempotent.
    """

    client = get_client()

    return client.get_or_create_collection(
        name=name
    )


def add_documents(
    collection,
    docs: list[str],
    embeddings: list[list[float]],
) -> None:
    """
    Insert documents and embeddings into a ChromaDB collection.

    Each document receives a generated UUID to ensure unique
    identifiers within the vector store.

    Args:
        collection:
            Target ChromaDB collection.

        docs:
            Documents to store.

        embeddings:
            Embedding vectors corresponding to each document.

    Notes:
        - Document and embedding counts must match.
        - Duplicate semantic memories are not automatically
          deduplicated.
        - UUID generation is non-deterministic.
    """

    ids = [
        str(uuid.uuid4())
        for _ in docs
    ]

    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids,
    )


def query_collection(
    collection,
    query_embedding: list[float],
    k: int = 3,
    topic: str | None = None,
    memory_type: str | None = None,
    min_importance: float | None = None,
) -> dict:
    """
    Execute a semantic vector similarity query against a collection.

    Retrieval combines dense vector similarity search with optional
    metadata constraints to support controllable semantic retrieval.

    Supported filters include:
        - topic filtering
        - memory type filtering
        - importance threshold filtering

    Args:
        collection:
            Target ChromaDB collection.

        query_embedding:
            Embedding vector representing the retrieval query.

        k:
            Maximum number of nearest neighbors to retrieve.

        topic:
            Optional topic constraint.

        memory_type:
            Optional semantic memory category constraint.

        min_importance:
            Optional minimum importance threshold.

    Returns:
        Raw ChromaDB query response containing retrieved
        documents, metadata, distances, and identifiers.

    Notes:
        - Lower vector distance indicates higher semantic similarity.
        - Metadata filtering is deterministic.
        - Vector similarity retrieval is probabilistic.
    """

    where = {}

    if topic:
        where["topic"] = topic.lower()

    if memory_type:
        where["memory_type"] = memory_type.lower()

    if min_importance is not None:
        where["importance"] = {
            "$gte": float(min_importance)
        }

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where if where else None,
    )
