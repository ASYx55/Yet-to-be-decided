import json
import os
from pathlib import Path
from typing import Optional

from .model import Session, Turn

BASE_DIR = Path(os.getenv("DATA_DIR", "data/students"))


class ConvoLogStore:

    def __init__(self):
        BASE_DIR.mkdir(parents=True, exist_ok=True)

    def session_path(self, student_id: str, session_id: str) -> Path:
        
        folder = BASE_DIR / student_id
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{session_id}.json"

    def student_folder(self, student_id: str) -> Path:
        return BASE_DIR / student_id
    
    def save_session(self, session: Session) -> None:
        path = self.session_path(session.student_id, session.session_id)
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load_session(self, student_id: str, session_id: str) -> Optional[Session]:
        path = self.session_path(student_id, session_id)
        if not path.exists():
            return None
        with open(path, "r") as f:
            return Session.from_dict(json.load(f))

    def get_student_session_ids(self, student_id: str) -> list[str]:
        
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
        
        session_ids = self.get_student_session_ids(student_id)
        sessions = []
        for sid in session_ids:
            s = self.load_session(student_id, sid)
            if s:
                sessions.append(s)
        return sessions

    def delete_session(self, student_id: str, session_id: str) -> None:
        path = self.session_path(student_id, session_id)
        if path.exists():
            path.unlink()

    def get_recent_turns(self, student_id: str, session_id: str, n: int = 20) -> list[Turn]:
        
        session = self.load_session(student_id, session_id)
        if session is None:
            return []
        return session.turns[-n:]