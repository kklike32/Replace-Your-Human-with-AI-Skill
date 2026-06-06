from pathlib import Path

from tracker.events import Event, EventType, Session, Summary
from tracker.storage.local_sqlite import LocalSQLiteRepository


def test_local_sqlite_repository_roundtrip(tmp_path: Path) -> None:
    db_path = tmp_path / "local_tracker.db"
    repository = LocalSQLiteRepository(db_path)

    session = repository.create_session(Session(session_name="test", sync_enabled=False))
    repository.save_event(
        Event(
            session_id=session.id,
            event_type=EventType.KEYBOARD_SHORTCUT,
            metadata={"shortcut": "ctrl+s"},
        )
    )
    repository.save_summary(
        Summary(
            session_id=session.id,
            pseudocode="1. User used shortcut ctrl+s.",
            suggestions=["This workflow appears repetitive."],
        )
    )

    loaded_session = repository.get_session(session.id)
    events = repository.get_events(session.id)
    summary = repository.get_summary(session.id)

    assert loaded_session is not None
    assert loaded_session.id == session.id
    assert len(events) == 1
    assert events[0].metadata["shortcut"] == "ctrl+s"
    assert summary is not None
    assert summary.session_id == session.id
