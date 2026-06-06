"""
Memory ingestion utilities for ChromaDB.

This module handles conversion of structured semantic memory objects
into embeddings and metadata records suitable for persistent storage
in a ChromaDB vector collection.

It bridges the gap between the internal SemanticMemory schema and
the low-level vector database format.

Copyright (c) 2026 suy0x1
"""

import uuid

from .embeddings import embed_batch
from .memory_models import SemanticMemory


def add_memories(collection, memories: list[SemanticMemory]) -> None:
    """
    Insert structured semantic memories into a ChromaDB collection.

    Each memory is transformed into:
        - document text
        - embedding vector
        - metadata payload
        - unique identifier

    Args:
        collection:
            Target ChromaDB collection instance.

        memories:
            List of SemanticMemory objects to persist.

    Returns:
        None

    Notes:
        - Embeddings are generated in batch for efficiency.
        - Metadata is serialized into ChromaDB-compatible format.
        - UUIDs are generated per memory to ensure uniqueness.
        - No deduplication or overwrite logic is applied.
    """

    documents = [memory.text for memory in memories]

    embeddings = embed_batch(documents)

    metadatas = []

    for memory in memories:
        metadata = {
            "topic": memory.topic.lower(),
            "memory_type": memory.memory_type.value.lower(),
            "importance": float(memory.importance),
            "confidence": float(memory.confidence),
            "frequency": int(memory.frequency),
            "created_at": memory.created_at.isoformat(),
            "last_accessed": memory.last_accessed.isoformat(),
        }

        if memory.learning_style is not None:
            metadata["learning_style"] = memory.learning_style

        if memory.student_id is not None:
            metadata["student_id"] = memory.student_id

        metadatas.append(metadata)

    ids = [str(uuid.uuid4()) for _ in memories]

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
