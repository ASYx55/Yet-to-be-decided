"""
Conversation session logging utilities.

This module provides the high-level API for recording student and
assistant messages during a tutoring conversation. It manages active
session lifecycle, latency tracking, topic threads, persistent saves,
and retrieval of conversation history for model context.

Features:
    - new session creation
    - existing session resume support
    - user and assistant turn logging
    - assistant latency measurement
    - topic thread tracking
    - Gemini-compatible context retrieval

Copyright (c) 2026 ASYx55
"""

import time
from typing import Optional
from .model import Session, Turn, Role
from .storage import ConvoLogStore


class ConvoLogger:
    """
    Handles conversation logging for a student session.

    This class manages starting, resuming, updating, and ending a conversation
    session. It stores user and assistant messages as Turn objects and persists
    session data using ConvoLogStore.
    """

    def __init__(self, student_id: str, session_id: Optional[str] = None):
        """
        Initialize a conversation logger.

        Args:
            student_id: Unique identifier for the student.
            session_id: Optional existing session ID to resume.

        Raises:
            ValueError: If a provided session ID cannot be found or has expired.
        """
        self.student_id = student_id
        self.store = ConvoLogStore()

        if session_id:
            self._session = self.store.load_session(student_id, session_id)
            if self._session is None:
                raise ValueError(f"Session {session_id} not found or expired.")
        else:
            self._session = None

        self._request_start_time: Optional[float] = None

    def start_session(self) -> str:
        """
        Start a new conversation session.

        Returns:
            The newly created session ID.
        """
        self._session = Session(student_id=self.student_id)
        self.store.save_session(self._session)
        print(f"[L1] Session started: {self._session.session_id}")
        return self._session.session_id

    def end_session(self, pg_conn=None) -> Session:
        """
        End the active conversation session.

        The session is closed, saved, and optionally flushed to PostgreSQL.

        Args:
            pg_conn: Optional PostgreSQL connection used for permanent storage.

        Returns:
            The completed Session object.
        """
        self._require_active_session()
        self._session.close()
        self.store.save_session(self._session)

        if pg_conn:
            self.store.flush_to_postgres(self._session, pg_conn)
            print(f"[L1] Session {self._session.session_id} flushed to Postgres.")

        print(
            f"[L1] Session ended. Turns: {self._session.turn_count}, "
            f"Duration: {self._session.duration_seconds:.1f}s"
        )
        return self._session

    def log_user_message(self, content: str, topic: Optional[str] = None) -> Turn:
        """
        Log a user message in the active session.

        This also starts latency tracking so the next assistant response can
        record how long it took to arrive.

        Args:
            content: Text content of the user's message.
            topic: Optional topic label for the message.

        Returns:
            The created user Turn.
        """
        self._require_active_session()
        self._request_start_time = time.monotonic()

        turn = Turn(role=Role.USER, content=content, topic=topic)
        self._session.add_turn(turn)

        if topic and topic not in self._session.topic_thread:
            self._session.topic_thread.append(topic)

        self.store.save_session(self._session)
        return turn

    def log_assistant_message(
        self,
        content: str,
        topic: Optional[str] = None,
        token_count: Optional[int] = None
    ) -> Turn:
        """
        Log an assistant message in the active session.

        If a user message was logged immediately before this response, latency
        is calculated in milliseconds.

        Args:
            content: Text content of the assistant's message.
            topic: Optional topic label for the message.
            token_count: Optional token count for the assistant response.

        Returns:
            The created assistant Turn.
        """
        self._require_active_session()

        latency_ms = None
        if self._request_start_time is not None:
            latency_ms = int((time.monotonic() - self._request_start_time) * 1000)
            self._request_start_time = None

        turn = Turn(
            role=Role.ASSISTANT,
            content=content,
            topic=topic,
            token_count=token_count,
            latency_ms=latency_ms
        )

        self._session.add_turn(turn)
        self.store.save_session(self._session)

        return turn

    def get_context_for_gemini(self, max_turns: int = 20) -> list[dict]:
        """
        Get recent conversation turns formatted for Gemini.

        Args:
            max_turns: Maximum number of recent turns to include.

        Returns:
            A list of Gemini-compatible message dictionaries.
        """
        self._require_active_session()
        recent = self._session.turns[-max_turns:]
        return [t.to_gemini_format() for t in recent]

    def get_full_history(self) -> list[Turn]:
        """
        Get the full conversation history.

        Returns:
            A list of all Turn objects in the active session.
        """
        self._require_active_session()
        return list(self._session.turns)

    def get_session_id(self) -> str:
        """
        Get the active session ID.

        Returns:
            The current session ID.
        """
        self._require_active_session()
        return self._session.session_id

    def get_topic_thread(self) -> list[str]:
        """
        Get the list of topics discussed in the session.

        Returns:
            A copy of the session's topic thread.
        """
        self._require_active_session()
        return list(self._session.topic_thread)

    def _require_active_session(self) -> None:
        """
        Ensure that a session is currently active.

        Raises:
            RuntimeError: If no session has been started or resumed.
        """
        if self._session is None:
            raise RuntimeError(
                "No active session. Call start_session() first, "
                "or pass session_id to resume an existing one."
            )
