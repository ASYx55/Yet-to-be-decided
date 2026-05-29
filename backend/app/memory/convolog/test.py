"""
Conversation logging package test suite.

This module verifies the behavior of the conversation log models,
JSON storage layer, and session logger. Tests isolate persistence by
redirecting storage writes into pytest temporary directories.

Coverage:
    - turn defaults and serialization
    - session lifecycle and reconstruction
    - JSON-backed save, load, list, and delete operations
    - logger session flow and resume behavior
    - Gemini context formatting

Copyright (c) 2026 ASYx55
"""

import sys
from pathlib import Path

import pytest

if __package__:
    from .model import Turn, Session, Role
    from .log import ConvoLogger
    from . import storage as storage_module
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from convolog.model import Turn, Session, Role
    from convolog.log import ConvoLogger
    from convolog import storage as storage_module


@pytest.fixture(autouse=True)
def temp_data_dir(tmp_path, monkeypatch):
    """Route storage writes to pytest's temporary directory."""
    monkeypatch.setattr(storage_module, "BASE_DIR", tmp_path / "students")


class TestTurn:
    def test_turn_creates_with_defaults(self):
        t = Turn(role=Role.USER, content="What is recursion?")
        assert t.role == Role.USER
        assert t.content == "What is recursion?"
        assert t.turn_id is not None
        assert t.timestamp is not None
        assert t.topic is None

    def test_turn_serialises_and_deserialises(self):
        t = Turn(
            role=Role.ASSISTANT,
            content="Recursion is...",
            topic="recursion",
            latency_ms=320,
        )
        t2 = Turn.from_dict(t.to_dict())
        assert t2.role == t.role
        assert t2.content == t.content
        assert t2.topic == t.topic
        assert t2.latency_ms == t.latency_ms

    def test_turn_to_gemini_format_user(self):
        t = Turn(role=Role.USER, content="Hello")
        gf = t.to_gemini_format()
        assert gf["role"] == "user"
        assert gf["parts"][0]["text"] == "Hello"

    def test_turn_to_gemini_format_assistant(self):
        t = Turn(role=Role.ASSISTANT, content="Hi there")
        assert t.to_gemini_format()["role"] == "model"


class TestSession:
    def test_session_creates_empty(self):
        s = Session(student_id="stu_001")
        assert s.student_id == "stu_001"
        assert s.turn_count == 0
        assert s.ended_at is None

    def test_session_add_turn(self):
        s = Session(student_id="stu_001")
        s.add_turn(Turn(role=Role.USER, content="Hello"))
        assert s.turn_count == 1

    def test_session_close(self):
        s = Session(student_id="stu_001")
        s.close()
        assert s.ended_at is not None
        assert s.duration_seconds is not None

    def test_session_round_trip(self):
        s = Session(student_id="stu_001")
        s.add_turn(Turn(role=Role.USER, content="Q1"))
        s.add_turn(Turn(role=Role.ASSISTANT, content="A1"))
        s2 = Session.from_dict(s.to_dict())
        assert s2.student_id == s.student_id
        assert s2.turn_count == 2
        assert s2.turns[0].content == "Q1"


class TestConversationLogStore:
    def test_save_and_load_session(self):
        store = storage_module.ConvoLogStore()

        s = Session(student_id="stu_001")
        s.add_turn(Turn(role=Role.USER, content="Hello"))
        store.save_session(s)

        loaded = store.load_session("stu_001", s.session_id)
        assert loaded is not None
        assert loaded.turn_count == 1
        assert loaded.turns[0].content == "Hello"

    def test_load_nonexistent_returns_none(self):
        store = storage_module.ConvoLogStore()
        result = store.load_session("stu_999", "fake-session-id")
        assert result is None

    def test_json_file_is_created_on_disk(self):
        store = storage_module.ConvoLogStore()

        s = Session(student_id="stu_001")
        store.save_session(s)

        expected_file = storage_module.BASE_DIR / "stu_001" / f"{s.session_id}.json"
        assert expected_file.exists()

    def test_get_student_session_ids(self):
        store = storage_module.ConvoLogStore()

        s1 = Session(student_id="stu_001")
        s2 = Session(student_id="stu_001")
        store.save_session(s1)
        store.save_session(s2)

        ids = store.get_student_session_ids("stu_001")
        assert s1.session_id in ids
        assert s2.session_id in ids

    def test_delete_session(self):
        store = storage_module.ConvoLogStore()

        s = Session(student_id="stu_001")
        store.save_session(s)
        store.delete_session("stu_001", s.session_id)

        assert store.load_session("stu_001", s.session_id) is None


class TestConversationLogger:
    def test_full_session_flow(self):
        logger = ConvoLogger(student_id="stu_123")
        logger.start_session()

        logger.log_user_message("What is a base case?", topic="recursion")
        logger.log_assistant_message("A base case is...", topic="recursion")

        turns = logger.get_full_history()
        assert len(turns) == 2
        assert turns[0].role == Role.USER
        assert turns[1].role == Role.ASSISTANT

    def test_session_persists_to_disk(self):
        logger = ConvoLogger(student_id="stu_123")
        session_id = logger.start_session()

        logger.log_user_message("Hello")
        logger.log_assistant_message("Hi!")

        file = storage_module.BASE_DIR / "stu_123" / f"{session_id}.json"
        assert file.exists()

    def test_session_can_be_resumed(self):
        logger1 = ConvoLogger(student_id="stu_123")
        session_id = logger1.start_session()
        logger1.log_user_message("Hello")
        logger1.log_assistant_message("Hi!")

        logger2 = ConvoLogger(student_id="stu_123", session_id=session_id)
        turns = logger2.get_full_history()
        assert len(turns) == 2
        assert turns[0].content == "Hello"

    def test_latency_is_recorded(self):
        logger = ConvoLogger(student_id="stu_123")
        logger.start_session()
        logger.log_user_message("Hello")
        turn = logger.log_assistant_message("Hi!")
        assert turn.latency_ms is not None
        assert turn.latency_ms >= 0

    def test_topic_thread_builds(self):
        logger = ConvoLogger(student_id="stu_123")
        logger.start_session()
        logger.log_user_message("What is recursion?", topic="recursion")
        logger.log_assistant_message("Recursion is...", topic="recursion")
        logger.log_user_message("What is a loop?", topic="loops")
        logger.log_assistant_message("A loop is...", topic="loops")

        thread = logger.get_topic_thread()
        assert "recursion" in thread
        assert "loops" in thread
        assert thread.index("recursion") < thread.index("loops")

    def test_gemini_context_format(self):
        logger = ConvoLogger(student_id="stu_123")
        logger.start_session()
        logger.log_user_message("Q1")
        logger.log_assistant_message("A1")
        logger.log_user_message("Q2")

        context = logger.get_context_for_gemini(max_turns=10)
        assert len(context) == 3
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "model"
        assert context[2]["parts"][0]["text"] == "Q2"

    def test_max_turns_truncation(self):
        logger = ConvoLogger(student_id="stu_123")
        logger.start_session()
        for i in range(30):
            logger.log_user_message(f"Q{i}")
            logger.log_assistant_message(f"A{i}")

        context = logger.get_context_for_gemini(max_turns=10)
        assert len(context) == 10

    def test_session_end(self):
        logger = ConvoLogger(student_id="stu_123")
        logger.start_session()
        logger.log_user_message("Hello")
        logger.log_assistant_message("Hi")
        session = logger.end_session()
        assert session.ended_at is not None
        assert session.duration_seconds >= 0

    def test_requires_active_session(self):
        logger = ConvoLogger(student_id="stu_123")
        with pytest.raises(RuntimeError, match="No active session"):
            logger.log_user_message("Hello")

    def test_resume_nonexistent_session_raises(self):
        with pytest.raises(ValueError, match="not found"):
            ConvoLogger(student_id="stu_123", session_id="fake-id")
