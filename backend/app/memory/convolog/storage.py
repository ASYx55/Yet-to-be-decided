"""
Persistent JSON conversation storage utilities.

This module provides the low-level persistence and retrieval layer
for conversation log sessions. It stores each session as a JSON file,
groups sessions by student ID, and supports recent-turn lookup for
context reconstruction.

Features:
    - disk-backed session persistence
    - student-scoped session folders
    - newest-first session listing
    - full session loading
    - recent turn retrieval
    - optional DATA_DIR-based storage configuration

Copyright (c) 2026 ASYx55
"""

import json
import os
from pathlib import Path
from typing import Optional

from .model import Session, Turn

BASE_DIR = Path(os.getenv("DATA_DIR", "data/students"))


class ConvoLogStore:
    """
    Persist and retrieve conversation sessions from local JSON files.

    The store is intentionally small and file-system backed. Each student
    receives a dedicated folder, and each session is stored as one JSON
    document named by session ID.
    """

    def __init__(self):
        """
        Create the base storage directory if it does not already exist.

        The base directory is resolved at module load time from DATA_DIR,
        falling back to data/students when no environment override exists.
        """
        BASE_DIR.mkdir(parents=True, exist_ok=True)

    def session_path(self, student_id: str, session_id: str) -> Path:
        """
        Build the JSON path for a student's session.

        The student's directory is created as needed.
        """
        folder = BASE_DIR / student_id
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{session_id}.json"

    def student_folder(self, student_id: str) -> Path:
        """
        Return the storage folder for a student.

        Args:
            student_id:
                Unique identifier for the student.

        Returns:
            Path to the student's session directory.
        """
        return BASE_DIR / student_id

    def save_session(self, session: Session) -> None:
        """
        Write a session to disk as formatted JSON.

        Args:
            session:
                Session object to serialize and persist.
        """
        path = self.session_path(session.student_id, session.session_id)
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load_session(self, student_id: str, session_id: str) -> Optional[Session]:
        """
        Load a session from disk.

        Args:
            student_id:
                Unique identifier for the student.

            session_id:
                Unique identifier for the conversation session.

        Returns:
            Reconstructed Session object when found, otherwise None.
        """
        path = self.session_path(student_id, session_id)
        if not path.exists():
            return None
        with open(path, "r") as f:
            return Session.from_dict(json.load(f))

    def get_student_session_ids(self, student_id: str) -> list[str]:
        """
        Return a student's session IDs.

        Args:
            student_id:
                Unique identifier for the student.

        Returns:
            Session IDs sorted by file modification time, newest first.
        """
        folder = self.student_folder(student_id)
        if not folder.exists():
            return []

        files = sorted(
            folder.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        return [f.stem for f in files]

    def get_all_sessions(self, student_id: str) -> list[Session]:
        """
        Load every stored session for a student.

        Args:
            student_id:
                Unique identifier for the student.

        Returns:
            List of reconstructed sessions ordered by newest file first.
        """
        session_ids = self.get_student_session_ids(student_id)
        sessions = []
        for sid in session_ids:
            s = self.load_session(student_id, sid)
            if s:
                sessions.append(s)
        return sessions

    def delete_session(self, student_id: str, session_id: str) -> None:
        """
        Delete a stored session if it exists.

        Args:
            student_id:
                Unique identifier for the student.

            session_id:
                Unique identifier for the conversation session.
        """
        path = self.session_path(student_id, session_id)
        if path.exists():
            path.unlink()

    def get_recent_turns(
        self,
        student_id: str,
        session_id: str,
        n: int = 20
    ) -> list[Turn]:
        """
        Return the latest turns from a session.

        Args:
            student_id:
                Unique identifier for the student.

            session_id:
                Unique identifier for the conversation session.

            n:
                Maximum number of recent turns to return.

        Returns:
            List of recent Turn objects, or an empty list if the session
            cannot be found.
        """
        session = self.load_session(student_id, session_id)
        if session is None:
            return []
        return session.turns[-n:]
