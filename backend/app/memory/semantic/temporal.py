"""
Temporal utilities for memory scoring.

Copyright (c) 2026 suy0x1
"""

import math
from datetime import datetime


def days_old(iso_time: str) -> int:
    """Return age in days from ISO timestamp."""
    created = datetime.fromisoformat(iso_time)
    return (datetime.utcnow() - created).days


def decay_score(age_days: int, decay_lambda: float = 0.03) -> float:
    """Exponential decay for recency scoring."""
    return math.exp(-decay_lambda * age_days)
