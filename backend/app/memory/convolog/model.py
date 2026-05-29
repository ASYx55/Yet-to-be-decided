"""
Conversation log data models.

This module defines the serializable data structures used by the
conversation logging system. It models participant roles, individual
conversation turns, and complete tutoring sessions that can be saved
to disk or reconstructed from JSON.

Features:
    - role-constrained message representation
    - timestamped conversation turns
    - session metadata and topic tracking
    - dictionary serialization and reconstruction
    - Gemini-compatible message conversion

Copyright (c) 2026 ASYx55
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class Role(str, Enum):
    """
    Represents the role of a participant in a conversation.

    Values:
        USER: A message written by the user or student.
        ASSISTANT: A message written by the AI assistant.
        SYSTEM: A system-level instruction or message.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Turn:
    """
    Represents a single conversation turn.

    A turn is one message in a conversation, including its speaker role,
    message content, timestamp, unique ID, and optional metadata such as
    topic, token count, and response latency.
    """

    role: Role
    content: str
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    topic: Optional[str] = None
    token_count: Optional[int] = None
    latency_ms: Optional[int] = None

    def to_dict(self) -> dict:
        """
        Convert the Turn object into a dictionary.

        Returns:
            dict: A dictionary representation of the turn.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Turn":
        """
        Create a Turn object from a dictionary.

        Args:
            d (dict): Dictionary containing turn data.

        Returns:
            Turn: A reconstructed Turn object.

        Note:
            The role value is converted from a string back into a Role enum.
        """
        d["role"] = Role(d["role"])
        return cls(**d)

    def to_gemini_format(self) -> dict:
        """
        Convert the turn into Gemini API-compatible message format.

        Gemini expects messages in the format:
            {
                "role": "user" or "model",
                "parts": [{"text": "..."}]
            }

        Returns:
            dict: The turn formatted for Gemini-style chat APIs.
        """
        return {
            "role": "user" if self.role == Role.USER else "model",
            "parts": [{"text": self.content}]
        }


@dataclass
class Session:
    """
    Represents a complete conversation session for a student.

    A session contains metadata such as the student ID, session ID,
    start and end timestamps, topic thread, and all conversation turns.
    """

    student_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    ended_at: Optional[str] = None
    turns: list[Turn] = field(default_factory=list)
    topic_thread: list[str] = field(default_factory=list)

    @property
    def turn_count(self) -> int:
        """
        Get the total number of turns in the session.

        Returns:
            int: Number of turns stored in the session.
        """
        return len(self.turns)

    @property
    def duration_seconds(self) -> Optional[float]:
        """
        Calculate the duration of the session in seconds.

        Returns:
            Optional[float]: Duration in seconds if the session has ended,
            otherwise None.
        """
        if not self.ended_at:
            return None

        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.ended_at)
        return (end - start).total_seconds()

    def add_turn(self, turn: Turn) -> None:
        """
        Add a new conversation turn to the session.

        Args:
            turn (Turn): The turn to add.
        """
        self.turns.append(turn)

    def close(self) -> None:
        """
        Mark the session as ended.

        Sets the ended_at timestamp to the current UTC time.
        """
        self.ended_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """
        Convert the Session object into a dictionary.

        This includes session metadata, the calculated turn count,
        topic thread, and all nested turns.

        Returns:
            dict: A dictionary representation of the session.
        """
        return {
            "student_id": self.student_id,
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "turn_count": self.turn_count,
            "topic_thread": self.topic_thread,
            "turns": [t.to_dict() for t in self.turns],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Session":
        """
        Create a Session object from a dictionary.

        Args:
            d (dict): Dictionary containing session data.

        Returns:
            Session: A reconstructed Session object.

        Note:
            Nested turn dictionaries are converted back into Turn objects.
            The stored turn_count is ignored because it can be recalculated.
        """
        turns = [Turn.from_dict(t) for t in d.pop("turns", [])]
        d.pop("turn_count", None)

        session = cls(**d)
        session.turns = turns
        return session
