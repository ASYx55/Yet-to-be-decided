"""
Conversation logging package public interface.

This package exposes the primary classes used to create, persist,
resume, and inspect student conversation sessions. It provides a
small facade over the data models and JSON-backed storage layer used
by the adaptive tutoring system.

Features:
    - session-oriented conversation logging
    - JSON-backed persistence
    - reusable conversation data models
    - Gemini-compatible context formatting
    - student-scoped session retrieval

Copyright (c) 2026 ASYx55
"""

from .log import ConvoLogger
from .model import Turn, Session, Role
from .storage import ConvoLogStore

__all__ = ["ConvoLogger", "Turn", "Session", "Role", "ConvoLogStore"]
