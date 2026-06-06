"""
Cognitive scoring utilities for semantic memory retrieval.

This module implements metadata-aware reranking logic used during
semantic memory retrieval. Scores combine semantic similarity with
cognitive relevance signals such as importance, confidence, recency,
and retrieval frequency.

Scoring Philosophy:
    - Semantic similarity is the dominant ranking factor
    - Metadata signals provide lightweight reranking adjustments
    - Weak semantic matches should not survive reranking
    - Frequently reinforced memories receive small boosts
    - Older memories gradually decay in retrieval priority

Copyright (c) 2026 suy0x1
"""

from .temporal import days_old
from .temporal import decay_score


def compute_memory_score(distance: float, metadata: dict) -> float:
    """
    Compute a cognitive relevance score for a retrieved memory.

    The scoring function combines semantic similarity with cognitive
    metadata signals to produce a final reranking score. Semantic
    relevance remains the dominant factor while metadata provides
    lightweight prioritization adjustments.

    Scoring Factors:
        - semantic similarity
        - memory importance
        - confidence score
        - temporal recency
        - retrieval frequency

    Args:
        distance:
            Vector similarity distance between the query embedding
            and the retrieved memory embedding.

        metadata:
            Metadata associated with the retrieved memory.

            Expected keys include:
                - ``importance``
                - ``confidence``
                - ``frequency``
                - ``created_at``

    Returns:
        Final cognitive relevance score between approximately
        0.0 and 1.0, where higher values indicate stronger
        retrieval relevance.

    Notes:
        - Lower vector distance implies higher semantic similarity.
        - Semantic similarity contributes the majority of the score.
        - Frequency boosts are intentionally capped to avoid
          runaway reinforcement bias.
        - Older memories gradually lose retrieval priority through
          temporal decay.
    """

    semantic_score = 1.0 - distance

    importance = metadata.get("importance", 0.5)
    confidence = metadata.get("confidence", 0.5)
    frequency = metadata.get("frequency", 1)

    age = days_old(metadata["created_at"])
    recency = decay_score(age)

    frequency_boost = min(frequency / 10, 1.0)

    final_score = (
        semantic_score * 0.75
        + importance * 0.10
        + confidence * 0.05
        + recency * 0.05
        + frequency_boost * 0.05
    )

    return final_score
