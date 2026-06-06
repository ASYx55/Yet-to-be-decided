"""
Semantic memory data model for ChromaDB storage.

Copyright (c) 2026 suy0x1
"""

from datetime import datetime
from pydantic import BaseModel
from .memory_types import MemoryType


class SemanticMemory(BaseModel):
    """
    Core schema representing a stored semantic memory.

    This model defines the minimal structure required for storing
    and retrieving educational memory signals in the vector store.
    """

    text: str
    topic: str
    memory_type: MemoryType

    importance: float = 0.5
    confidence: float = 0.5
    frequency: int = 1

    learning_style: str | None = None

    created_at: datetime = datetime.utcnow()
    last_accessed: datetime = datetime.utcnow()

    student_id: str | None = None
