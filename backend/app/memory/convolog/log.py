import time
from typing import Optional
from .model import Session, Turn, Role
from .storage import ConvoLogStore

class ConvoLogger:
    

    def __init__(self, student_id: str, session_id: Optional[str] = None):
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
        
        self._session = Session(student_id=self.student_id)
        self.store.save_session(self._session)
        print(f"[L1] Session started: {self._session.session_id}")
        return self._session.session_id

    def end_session(self, pg_conn=None) -> Session:
        
        self._require_active_session()
        self._session.close()
        self.store.save_session(self._session)

        if pg_conn:
            self.store.flush_to_postgres(self._session, pg_conn)
            print(f"[L1] Session {self._session.session_id} flushed to Postgres.")

        print(f"[L1] Session ended. Turns: {self._session.turn_count}, "
              f"Duration: {self._session.duration_seconds:.1f}s")
        return self._session

    def log_user_message(self, content: str, topic: Optional[str] = None) -> Turn:
       
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
        
        self._require_active_session()
        recent = self._session.turns[-max_turns:]
        return [t.to_gemini_format() for t in recent]

    def get_full_history(self) -> list[Turn]:
        self._require_active_session()
        return list(self._session.turns)

    def get_session_id(self) -> str:
        self._require_active_session()
        return self._session.session_id

    def get_topic_thread(self) -> list[str]:
        self._require_active_session()
        return list(self._session.topic_thread)

    def _require_active_session(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "No active session. Call start_session() first, "
                "or pass session_id to resume an existing one.")
            