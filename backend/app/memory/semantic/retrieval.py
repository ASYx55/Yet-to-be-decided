"""
Semantic retrieval and cognitive reranking utilities.

This module implements high-level semantic memory retrieval over
vector embeddings stored in ChromaDB. It combines semantic similarity
search with metadata-aware reranking to improve retrieval quality
for educational and adaptive learning systems.

Retrieval Pipeline:
    1. Embed the natural language query
    2. Retrieve semantic candidates from ChromaDB
    3. Apply metadata-based filtering
    4. Apply semantic distance thresholding
    5. Compute cognitive relevance scores
    6. Apply minimum score filtering
    7. Return ranked semantic memories

The retrieval system prioritizes precision over recall to reduce
irrelevant memory retrieval and improve downstream reasoning quality.

Copyright (c) 2026 suy0x1
"""

from .embeddings import embed_query
from .chroma_store import query_collection
from .scoring import compute_memory_score

MAX_DISTANCE = 0.49
MIN_SCORE = 0.40


def search(
    collection,
    query_text: str,
    k: int = 10,
    topic: str | None = None,
    memory_type: str | None = None,
    min_importance: float | None = None,
) -> list[dict]:
    """
    Retrieve and rerank semantic memories for a natural language query.

    The search process combines vector similarity retrieval with
    metadata-aware cognitive reranking. Retrieved candidates are
    filtered using semantic distance and relevance score thresholds
    before being sorted by final retrieval quality.

    Args:
        collection:
            ChromaDB collection instance used for vector retrieval.

        query_text:
            Natural language query describing the desired memory.

        k:
            Maximum number of semantic candidates to retrieve from
            the vector store before reranking. Defaults to 10.

        topic:
            Optional topic filter used to restrict retrieval to
            memories associated with a specific subject or concept.

        memory_type:
            Optional memory category filter such as "weakness",
            "strength", or "misconception".

        min_importance:
            Optional minimum importance threshold for candidate
            memories.

    Returns:
        A list of ranked semantic memory dictionaries containing:

        - ``text``:
            Original memory text.

        - ``metadata``:
            Associated memory metadata.

        - ``distance``:
            Vector similarity distance from the query embedding.

        - ``score``:
            Final cognitive relevance score.

    Notes:
        - Lower semantic distance indicates higher similarity.
        - Higher reranking scores indicate stronger relevance.
        - Weak matches are intentionally discarded to prioritize
          retrieval precision over recall.
        - Returning no memories is preferred over returning
          misleading or weakly related memories.

    Example:
        >>> results = search(
        ...     collection,
        ...     "I don't understand recursive DFS",
        ...     k=5,
        ... )
    """

    query_embedding = embed_query(query_text)

    results = query_collection(
        collection=collection,
        query_embedding=query_embedding,
        k=k,
        topic=topic,
        memory_type=memory_type,
        min_importance=min_importance,
    )

    ranked = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if distance > MAX_DISTANCE:
            continue

        score = compute_memory_score(
            distance=distance,
            metadata=metadata,
        )

        if score < MIN_SCORE:
            continue

        ranked.append(
            {
                "text": document,
                "metadata": metadata,
                "distance": distance,
                "score": score,
            }
        )

    ranked.sort(
        key=lambda memory: memory["score"],
        reverse=True,
    )

    return ranked
