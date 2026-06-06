from datetime import datetime, timedelta, timezone
from pathlib import Path

from tracker.chunker import ActivityChunker
from tracker.events import Event, EventType, ScreenshotRecord


def test_screenshot_scheduling_every_two_seconds() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    chunker = ActivityChunker("session-1", now_provider=lambda: start)

    assert chunker.should_capture_screenshot(start) is True
    chunker.mark_screenshot_captured(
        ScreenshotRecord(session_id="session-1", local_path="/tmp/screen-1.png"),
        start,
    )
    assert chunker.should_capture_screenshot(start + timedelta(seconds=1)) is False
    assert chunker.should_capture_screenshot(start + timedelta(seconds=2)) is True


def test_chunk_creation_every_six_seconds() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    chunker = ActivityChunker("session-1", now_provider=lambda: start)
    chunker.add_event(
        Event(
            session_id="session-1",
            event_type=EventType.ACTIVE_WINDOW,
            timestamp=start,
            app_name="Safari",
            window_title="Example",
        )
    )
    chunker.mark_screenshot_captured(
        ScreenshotRecord(session_id="session-1", local_path="/tmp/screen-1.png"),
        start,
    )

    assert chunker.build_chunk(start + timedelta(seconds=5)) is None
    chunk = chunker.build_chunk(start + timedelta(seconds=6))

    assert chunk is not None
    assert chunk.chunk_index == 0
    assert chunk.screenshots == [Path("/tmp/screen-1.png")]
    assert chunk.active_windows[0]["app_name"] == "Safari"


def test_reset_clears_active_buffer_after_summary() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    chunker = ActivityChunker("session-1", now_provider=lambda: start)
    chunker.add_event(
        Event(session_id="session-1", event_type=EventType.MOUSE_CLICK, timestamp=start)
    )
    chunker.reset_chunk_buffer(start + timedelta(seconds=6))

    assert chunker.build_chunk(start + timedelta(seconds=7), force=True) is None


def test_force_build_flushes_partial_chunk() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    chunker = ActivityChunker("session-1", now_provider=lambda: start)
    chunker.add_event(
        Event(
            session_id="session-1",
            event_type=EventType.KEYBOARD_SHORTCUT,
            timestamp=start,
            metadata={"shortcut": "cmd+s"},
        )
    )

    chunk = chunker.build_chunk(start + timedelta(seconds=2), force=True)

    assert chunk is not None
    assert chunk.keyboard_shortcuts[0]["shortcut"] == "cmd+s"
