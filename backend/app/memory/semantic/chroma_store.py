"""
ChromaDB Vector Store Module.

Provides functions for creating collections, inserting embeddings,
and performing semantic similarity search using ChromaDB.

Copyright (c) 2026 suy0x1
"""

import uuid
import chromadb


def create_collection(name="memory"):
    """
    Create a new ChromaDB collection.

    A collection is similar to a table in SQL databases.
    It stores:
        - documents
        - embeddings
        - ids
        - optional metadata

    Args:
        name (str, optional):
            Name of the collection.
            Defaults to "memory".

    Returns:
        chromadb.Collection:
            A ChromaDB collection object.

    Example:
        >>> collection = create_collection("student_memory")

    Notes:
        - Uses in-memory ChromaDB storage by default.
        - Collection data disappears when program exits unless
          persistent storage is configured.
    """
    client = chromadb.Client()
    return client.create_collection(name=name)


def add_documents(collection, docs, embeddings):
    """
    Insert documents and embeddings into a ChromaDB collection.

    Each document receives a randomly generated UUID to prevent
    ID collisions during multiple insert operations.

    Args:
        collection:
            The ChromaDB collection object.

        docs (list[str]):
            List of text documents to store.

        embeddings (list[list[float]]):
            Vector embeddings corresponding to each document.

    Returns:
        None

    Example:
        >>> docs = [
        ...     "Student struggles with recursion",
        ...     "Student likes visual explanations"
        ... ]
        >>> embeddings = embed_batch(docs)
        >>> add_documents(collection, docs, embeddings)

    Notes:
        - Number of embeddings must equal number of documents.
        - Embeddings should already be generated beforehand.
        - UUIDs ensure uniqueness across all insertions.
    """
    ids = [str(uuid.uuid4()) for _ in docs]

    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids
    )


def query_collection(collection, query_embedding, k=3):
    """
    Perform semantic similarity search in ChromaDB.

    The query embedding is compared against all stored
    embeddings using vector similarity distance.

    Args:
        collection:
            ChromaDB collection object.

        query_embedding (list[float]):
            Embedding vector representing the query.

        k (int, optional):
            Number of nearest results to retrieve.
            Defaults to 3.

    Returns:
        dict:
            ChromaDB query response containing:
                - ids
                - documents
                - distances
                - metadata

    Example:
        >>> query_emb = embed_text(
        ...     "I don't understand recursion"
        ... )
        >>> results = query_collection(
        ...     collection,
        ...     query_emb,
        ...     k=3
        ... )

    Notes:
        - Lower distance means higher semantic similarity.
        - Retrieval is based purely on embedding proximity.
    """
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
