"""
Cognitive state construction utilities.

This module aggregates retrieved semantic memories into a structured
representation of a learner's cognitive profile. It groups signals
such as weaknesses, strengths, preferences, misconceptions, and
successful strategies to support downstream personalization and
adaptive reasoning.

Copyright (c) 2026 suy0x1
"""

from collections import defaultdict


def build_cognitive_state(memories: list[dict]) -> dict:
    """
    Construct a structured cognitive state from retrieved memories.

    This function processes a list of semantic memories and organizes
    them into categorized cognitive signals. It also accumulates
    per-topic confidence scores to reflect inferred certainty levels.

    Args:
        memories:
            List of memory dictionaries containing:
                - text: memory content
                - metadata: includes topic, memory_type, confidence
                - score: optional retrieval score for strategies

    Returns:
        A dictionary containing:
            - weaknesses: unique topics where weaknesses were observed
            - strengths: unique topics representing strong performance
            - preferences: raw preference statements
            - misconceptions: misconception memory texts
            - successful_strategies: structured strategy entries
            - confidence: aggregated confidence per topic

    Notes:
        - Weaknesses and strengths are deduplicated by topic.
        - Preferences and misconceptions retain full text entries.
        - Confidence values are accumulated across memories per topic.
        - Only memories with valid topic and memory_type are included.
    """

    weaknesses = []
    strengths = []
    preferences = []
    misconceptions = []
    successful_strategies = []

    confidence_map = defaultdict(float)

    for memory in memories:
        metadata = memory.get("metadata", {})

        mtype = metadata.get("memory_type")
        topic = metadata.get("topic")

        if not topic or not mtype:
            continue

        if mtype == "weakness":
            weaknesses.append(topic)

        elif mtype == "strength":
            strengths.append(topic)

        elif mtype == "preference":
            preferences.append(memory["text"])

        elif mtype == "misconception":
            misconceptions.append(memory["text"])

        elif mtype == "successful_strategy":
            successful_strategies.append(
                {
                    "topic": topic,
                    "strategy": memory["text"],
                    "score": memory["score"],
                }
            )

        confidence_map[topic] += metadata.get(
            "confidence",
            0.5
        )

    return {
        "weaknesses": list(set(weaknesses)),
        "strengths": list(set(strengths)),
        "preferences": preferences,
        "misconceptions": misconceptions,
        "successful_strategies": successful_strategies,
        "confidence": dict(confidence_map),
    }
