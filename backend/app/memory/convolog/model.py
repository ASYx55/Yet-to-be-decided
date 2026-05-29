from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class Turn:
    
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
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Turn":
        d["role"] = Role(d["role"])
        return cls(**d)

    def to_gemini_format(self) -> dict:
        return {
            "role": "user" if self.role == Role.USER else "model",
            "parts": [{"text": self.content}]
        }


@dataclass
class Session:
    
    student_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    ended_at: Optional[str] = None
    turns: list[Turn] = field(default_factory=list)
    topic_thread: list[str] = field(default_factory=list)  # e.g. ["recursion", "base cases"]

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def duration_seconds(self) -> Optional[float]:
        if not self.ended_at:
            return None
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.ended_at)
        return (end - start).total_seconds()

    def add_turn(self, turn: Turn) -> None:
        self.turns.append(turn)

    def close(self) -> None:
        self.ended_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
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
        turns = [Turn.from_dict(t) for t in d.pop("turns", [])]
        d.pop("turn_count", None)
        session = cls(**d)
        session.turns = turns
        return session