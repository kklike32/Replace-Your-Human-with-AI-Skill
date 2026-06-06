from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from datetime import datetime, timezone
from pathlib import Path

from tracker.events import ActivityChunk, Event, EventType, ScreenshotRecord


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ActivityChunker:
    def __init__(
        self,
        session_id: str,
        screenshot_interval_seconds: int = 2,
        chunk_interval_seconds: int = 6,
        now_provider: Callable[[], datetime] | None = None,
    ):
        self.session_id = session_id
        self.screenshot_interval_seconds = screenshot_interval_seconds
        self.chunk_interval_seconds = chunk_interval_seconds
        self._now_provider = now_provider or _utc_now
        self._chunk_started_at = self._now_provider()
        self._next_screenshot_at = self._chunk_started_at
        self._chunk_index = 0
        self._events: list[Event] = []
        self._screenshots: list[ScreenshotRecord] = []

    def should_capture_screenshot(self, now: datetime | None = None) -> bool:
        current = now or self._now_provider()
        return current >= self._next_screenshot_at

    def mark_screenshot_captured(
        self,
        screenshot: ScreenshotRecord,
        now: datetime | None = None,
    ) -> None:
        self._screenshots.append(screenshot)
        self.skip_screenshot(now)

    def skip_screenshot(self, now: datetime | None = None) -> None:
        current = now or self._now_provider()
        self._next_screenshot_at = current + timedelta(seconds=self.screenshot_interval_seconds)

    def add_event(self, event: Event) -> None:
        self._events.append(event)

    def should_build_chunk(self, now: datetime | None = None) -> bool:
        current = now or self._now_provider()
        if not (self._events or self._screenshots):
            return False
        return (current - self._chunk_started_at).total_seconds() >= self.chunk_interval_seconds

    def build_chunk(
        self,
        now: datetime | None = None,
        force: bool = False,
    ) -> ActivityChunk | None:
        current = now or self._now_provider()
        if not (self._events or self._screenshots):
            return None
        if not force and not self.should_build_chunk(current):
            return None

        screenshots = [Path(record.local_path) for record in self._screenshots]
        mouse_events = [
            {
                "timestamp": event.timestamp.isoformat(),
                "button": event.metadata.get("button"),
                "x": event.metadata.get("x"),
                "y": event.metadata.get("y"),
            }
            for event in self._events
            if event.event_type == EventType.MOUSE_CLICK
        ]
        keyboard_shortcuts = [
            {
                "timestamp": event.timestamp.isoformat(),
                "shortcut": event.metadata.get("shortcut"),
            }
            for event in self._events
            if event.event_type == EventType.KEYBOARD_SHORTCUT
        ]
        active_windows = [
            {
                "timestamp": event.timestamp.isoformat(),
                "app_name": event.app_name,
                "window_title": event.window_title,
            }
            for event in self._events
            if event.event_type in {EventType.ACTIVE_WINDOW, EventType.SESSION_START}
        ]
        ocr_text = [
            str(event.metadata.get("text"))
            for event in self._events
            if event.event_type == EventType.OCR_TEXT and event.metadata.get("text")
        ]
        return ActivityChunk(
            session_id=self.session_id,
            chunk_index=self._chunk_index,
            started_at=self._chunk_started_at.isoformat(),
            ended_at=current.isoformat(),
            screenshots=screenshots,
            mouse_events=mouse_events,
            keyboard_shortcuts=keyboard_shortcuts,
            active_windows=active_windows,
            ocr_text=ocr_text,
        )

    def reset_chunk_buffer(self, now: datetime | None = None) -> None:
        current = now or self._now_provider()
        self._events.clear()
        self._screenshots.clear()
        self._chunk_index += 1
        self._chunk_started_at = current
        self._next_screenshot_at = current + timedelta(seconds=self.screenshot_interval_seconds)
