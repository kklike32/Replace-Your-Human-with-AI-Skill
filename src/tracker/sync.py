from __future__ import annotations

from datetime import datetime

from tracker.config import TrackerConfig
from tracker.events import EventType
from tracker.storage.insforge_client import InsForgeClient
from tracker.storage.local_sqlite import LocalSQLiteRepository


class SyncService:
    def __init__(
        self,
        repository: LocalSQLiteRepository,
        client: InsForgeClient,
        config: TrackerConfig,
    ) -> None:
        self.repository = repository
        self.client = client
        self.config = config

    def sync_all(self) -> dict[str, int]:
        synced_sessions = 0
        synced_events = 0
        synced_screenshots = 0
        synced_summaries = 0

        for session in self.repository.list_unsynced_sessions():
            cloud_session_id = session.cloud_id
            if not cloud_session_id:
                created = self.client.create_session(
                    {
                        "id": session.id,
                        "user_id": session.user_id,
                        "started_at": session.started_at.isoformat(),
                        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                        "session_name": session.session_name,
                        "device_name": session.device_name,
                        "os_name": session.os_name,
                        "sync_enabled": session.sync_enabled,
                    }
                )
                cloud_session_id = created.get("id", session.id)
            self.repository.mark_session_synced(session.id, cloud_session_id)
            synced_sessions += 1

            for event in self.repository.list_unsynced_events(session.id):
                payload = {
                    "id": event.id,
                    "session_id": cloud_session_id,
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type.value,
                    "app_name": event.app_name,
                    "window_title": event.window_title,
                    "metadata": event.metadata,
                }
                created_event = self.client.insert_event(payload)
                self.repository.mark_event_synced(event.id, created_event.get("id"))
                synced_events += 1

            if self.config.enable_screenshot_upload:
                for screenshot in self.repository.list_unsynced_screenshots(session.id):
                    storage_path = screenshot.storage_path or self._make_storage_path(
                        session.user_id,
                        session.id,
                        screenshot.captured_at,
                    )
                    self.client.upload_screenshot(
                        local_path=screenshot.local_path,
                        storage_path=storage_path,
                        bucket=self.config.insforge_storage_bucket,
                    )
                    self.repository.mark_screenshot_synced(screenshot.id, storage_path)
                    synced_screenshots += 1

            for summary in self.repository.list_unsynced_summaries(session.id):
                payload = {
                    "id": summary.id,
                    "session_id": cloud_session_id,
                    "pseudocode": summary.pseudocode,
                    "suggestions": summary.suggestions,
                }
                created_summary = self.client.save_summary(payload)
                self.repository.mark_summary_synced(summary.id, created_summary.get("id"))
                synced_summaries += 1

        return {
            "sessions": synced_sessions,
            "events": synced_events,
            "screenshots": synced_screenshots,
            "summaries": synced_summaries,
        }

    def _make_storage_path(
        self,
        user_id: str | None,
        session_id: str,
        captured_at: datetime,
    ) -> str:
        user_segment = user_id or "anonymous"
        ts = captured_at.strftime("%Y%m%dT%H%M%S%fZ")
        return f"users/{user_segment}/sessions/{session_id}/{ts}.png"

    def mark_local_only_events_as_synced(self, session_id: str) -> None:
        if self.config.enable_screenshot_upload:
            return
        for screenshot in self.repository.list_unsynced_screenshots(session_id):
            self.repository.mark_screenshot_synced(screenshot.id, screenshot.storage_path)

    def record_summary_events(self, session_id: str) -> None:
        from tracker.events import Event

        self.repository.save_event(Event(session_id=session_id, event_type=EventType.PSEUDOCODE_GENERATED))
        self.repository.save_event(Event(session_id=session_id, event_type=EventType.SUGGESTION_GENERATED))
