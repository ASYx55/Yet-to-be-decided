"""
Memory type schema for semantic memory classification.

Copyright (c) 2026 suy0x1
"""

from enum import Enum

class MemoryType(str, Enum):
    """
    Enum representing categories of semantic memories.

    Used to classify stored memory signals for retrieval,
    filtering, and cognitive reranking.
    """

    WEAKNESS = "weakness"
    STRENGTH = "strength"
    MISCONCEPTION = "misconception"
    PREFERENCE = "preference"
    SUCCESSFUL_STRATEGY = "successful_strategy"
    PROGRESS = "progress"
    CONCEPT = "concept"
