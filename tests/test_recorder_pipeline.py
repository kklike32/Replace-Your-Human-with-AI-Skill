from datetime import datetime, timedelta, timezone

from tracker.chunker import ActivityChunker
from tracker.config import TrackerConfig
from tracker.events import Event, EventType, FinalPseudocode, ScreenshotRecord, Session
from tracker.llm.mock import MockLLMClient
from tracker.recorder import SessionRecorder
from tracker.storage.local_sqlite import LocalSQLiteRepository


class _DummyClient:
    def __init__(self) -> None:
        self.summary_payloads = []
        self.final_payloads = []
        self.insight_payloads = []
        self.template_payloads = []
        self.handoff_payloads = []
        self.search_payloads = []

    def create_session(self, payload: dict) -> dict:
        return {"id": payload["id"]}

    def upload_chunk_summary(self, payload: dict) -> dict:
        self.summary_payloads.append(payload)
        return {"id": payload["id"]}

    def upload_final_pseudocode(self, payload: dict) -> dict:
        self.final_payloads.append(payload)
        return {"id": payload["id"]}

    def upload_workflow_insight(self, payload: dict) -> dict:
        self.insight_payloads.append(payload)
        return {"id": payload["id"]}

    def upload_workflow_template(self, payload: dict) -> dict:
        self.template_payloads.append(payload)
        return {"id": payload["id"]}

    def upload_agent_handoff_draft(self, payload: dict) -> dict:
        self.handoff_payloads.append(payload)
        return {"id": payload["id"]}

    def upload_search_index_record(self, payload: dict) -> dict:
        self.search_payloads.append(payload)
        return {"id": payload["id"]}


def test_recorder_generates_local_raw_data_and_remote_summaries_only(tmp_path) -> None:
    repository = LocalSQLiteRepository(tmp_path / "local_tracker.db")
    config = TrackerConfig(
        db_path=tmp_path / "local_tracker.db",
        screenshot_dir=tmp_path / "screenshots",
        export_dir=tmp_path / "exports",
        enable_cloud_sync=True,
        llm_provider="mock",
    )
    dummy_client = _DummyClient()
    recorder = SessionRecorder(config, repository, MockLLMClient(), dummy_client)

    session = repository.create_session(Session(id="session-1", sync_enabled=True))
    recorder.state.session_id = session.id
    now = datetime.now(timezone.utc)
    recorder._chunker = ActivityChunker(session.id, now_provider=lambda: now)

    event = repository.save_event(
        Event(
            session_id=session.id,
            event_type=EventType.ACTIVE_WINDOW,
            app_name="Chrome",
            window_title="Docs",
            timestamp=now,
        )
    )
    recorder._chunker.add_event(event)
    screenshot = repository.save_screenshot(
        ScreenshotRecord(
            session_id=session.id,
            local_path=str(tmp_path / "frame.png"),
            captured_at=now,
            ocr_text="Visible document heading",
        )
    )
    recorder._chunker.mark_screenshot_captured(screenshot, now)
    ocr_event = repository.save_event(
        Event(
            session_id=session.id,
            event_type=EventType.OCR_TEXT,
            metadata={"text": "Visible document heading"},
            timestamp=now,
        )
    )
    recorder._chunker.add_event(ocr_event)

    recorder._process_due_chunk(now + timedelta(seconds=6))
    summaries = repository.get_chunk_summaries(session.id)
    recorder._upload_chunk_summary(summaries[0])
    final = repository.save_final_pseudocode(
        FinalPseudocode(
            session_id=session.id,
            pseudocode=["Step 1. Review Docs in Chrome."],
            plain_text="1. Review Docs in Chrome.",
            suggestions=["Save the recurring workflow."],
        )
    )
    recorder._upload_final_pseudocode(final)

    assert repository.get_events(session.id)
    assert repository.get_screenshots(session.id)
    assert summaries
    assert dummy_client.summary_payloads
    assert dummy_client.final_payloads
    assert "summary" in dummy_client.summary_payloads[0]
    assert "pseudocode" not in dummy_client.summary_payloads[0]
    assert "pseudocode" in dummy_client.final_payloads[0]
    assert "ocr_text" not in dummy_client.final_payloads[0]
    assert "screenshots" not in dummy_client.final_payloads[0]


def test_recorder_purges_expired_raw_data_after_summary(tmp_path) -> None:
    repository = LocalSQLiteRepository(tmp_path / "local_tracker.db")
    config = TrackerConfig(
        db_path=tmp_path / "local_tracker.db",
        screenshot_dir=tmp_path / "screenshots",
        export_dir=tmp_path / "exports",
        enable_cloud_sync=False,
        llm_provider="mock",
        raw_data_ttl_seconds=300,
    )
    recorder = SessionRecorder(config, repository, MockLLMClient(), None)

    session = repository.create_session(Session(id="session-ttl", sync_enabled=False))
    recorder.state.session_id = session.id
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(minutes=10)
    recorder._chunker = ActivityChunker(session.id, now_provider=lambda: now)

    old_screenshot_path = tmp_path / "old_frame.png"
    old_screenshot_path.write_bytes(b"png")

    repository.save_event(
        Event(
            session_id=session.id,
            event_type=EventType.MOUSE_CLICK,
            timestamp=old_time,
            metadata={"x": 10, "y": 20, "button": "left"},
        )
    )
    repository.save_screenshot(
        ScreenshotRecord(
            session_id=session.id,
            local_path=str(old_screenshot_path),
            captured_at=old_time,
        )
    )

    event = repository.save_event(
        Event(
            session_id=session.id,
            event_type=EventType.ACTIVE_WINDOW,
            app_name="Chrome",
            window_title="Docs",
            timestamp=now,
        )
    )
    recorder._chunker.add_event(event)
    screenshot = repository.save_screenshot(
        ScreenshotRecord(
            session_id=session.id,
            local_path=str(tmp_path / "fresh_frame.png"),
            captured_at=now,
            ocr_text="Visible document heading",
        )
    )
    recorder._chunker.mark_screenshot_captured(screenshot, now)

    recorder._process_due_chunk(now + timedelta(seconds=6))

    assert repository.get_chunk_summaries(session.id)
    assert old_screenshot_path.exists() is False
    remaining_events = repository.get_events(session.id)
    assert all(event.event_type != EventType.MOUSE_CLICK for event in remaining_events)
