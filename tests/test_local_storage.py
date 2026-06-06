from pathlib import Path

from tracker.events import ChunkSummary, Event, EventType, FinalPseudocode, Session
from tracker.storage.local_sqlite import LocalSQLiteRepository


def test_local_sqlite_summary_roundtrip(tmp_path: Path) -> None:
    repository = LocalSQLiteRepository(tmp_path / "local_tracker.db")
    session = repository.create_session(Session(session_name="test", sync_enabled=False))

    repository.save_event(
        Event(
            session_id=session.id,
            event_type=EventType.KEYBOARD_SHORTCUT,
            metadata={"shortcut": "ctrl+s"},
        )
    )
    repository.save_chunk_summary(
        ChunkSummary(
            session_id=session.id,
            chunk_index=0,
            started_at="2026-01-01T00:00:00+00:00",
            ended_at="2026-01-01T00:00:06+00:00",
            summary="Edited a document.",
            observed_apps=["Word"],
            confidence="high",
        )
    )
    repository.save_final_pseudocode(
        FinalPseudocode(
            session_id=session.id,
            pseudocode=["Step 1. Edit the document."],
            plain_text="1. Edit the document.",
            suggestions=["Automate the template."],
        )
    )

    loaded_session = repository.get_session(session.id)
    events = repository.get_events(session.id)
    summaries = repository.get_chunk_summaries(session.id)
    final = repository.get_final_pseudocode(session.id)

    assert loaded_session is not None
    assert loaded_session.id == session.id
    assert len(events) == 1
    assert len(summaries) == 1
    assert summaries[0].observed_apps == ["Word"]
    assert final is not None
    assert final.pseudocode == ["Step 1. Edit the document."]


def test_local_sqlite_unsynced_summary_bookkeeping(tmp_path: Path) -> None:
    repository = LocalSQLiteRepository(tmp_path / "local_tracker.db")
    session = repository.create_session(Session(sync_enabled=True))
    summary = repository.save_chunk_summary(
        ChunkSummary(
            session_id=session.id,
            chunk_index=1,
            started_at="2026-01-01T00:00:06+00:00",
            ended_at="2026-01-01T00:00:12+00:00",
            summary="Reviewed a dashboard.",
            observed_apps=["Chrome"],
            confidence="medium",
        )
    )
    final = repository.save_final_pseudocode(
        FinalPseudocode(
            session_id=session.id,
            pseudocode=["Step 1. Review the dashboard."],
            plain_text="1. Review the dashboard.",
            suggestions=["Save the filtered view."],
        )
    )

    assert len(repository.list_unsynced_chunk_summaries(session.id)) == 1
    assert len(repository.list_unsynced_final_pseudocode(session.id)) == 1

    repository.mark_chunk_summary_synced(summary.id, "remote-summary")
    repository.mark_final_pseudocode_synced(final.id, "remote-final")

    assert repository.list_unsynced_chunk_summaries(session.id) == []
    assert repository.list_unsynced_final_pseudocode(session.id) == []
