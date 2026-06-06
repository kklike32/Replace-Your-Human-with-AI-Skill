from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from tracker.events import Event, EventType, ScreenshotRecord, Session, Summary
from tracker.storage.repository import TrackerRepository


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LocalSQLiteRepository(TrackerRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    session_name TEXT,
                    device_name TEXT,
                    os_name TEXT,
                    sync_enabled INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    cloud_id TEXT,
                    synced INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    app_name TEXT,
                    window_title TEXT,
                    metadata TEXT NOT NULL,
                    synced INTEGER NOT NULL DEFAULT 0,
                    cloud_id TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS screenshots (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    event_id TEXT,
                    local_path TEXT NOT NULL,
                    storage_path TEXT,
                    ocr_text TEXT,
                    captured_at TEXT NOT NULL,
                    synced INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id),
                    FOREIGN KEY(event_id) REFERENCES events(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS summaries (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    pseudocode TEXT NOT NULL,
                    suggestions TEXT NOT NULL,
                    synced INTEGER NOT NULL DEFAULT 0,
                    cloud_id TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )

    def create_session(self, session: Session) -> Session:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, user_id, started_at, ended_at, session_name, device_name, os_name,
                                      sync_enabled, status, cloud_id, synced, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.user_id,
                    session.started_at.isoformat(),
                    session.ended_at.isoformat() if session.ended_at else None,
                    session.session_name,
                    session.device_name,
                    session.os_name,
                    int(session.sync_enabled),
                    session.status,
                    session.cloud_id,
                    int(session.synced),
                    session.created_at.isoformat(),
                ),
            )
        return session

    def update_session(self, session: Session) -> Session:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET user_id = ?, started_at = ?, ended_at = ?, session_name = ?, device_name = ?, os_name = ?,
                    sync_enabled = ?, status = ?, cloud_id = ?, synced = ?
                WHERE id = ?
                """,
                (
                    session.user_id,
                    session.started_at.isoformat(),
                    session.ended_at.isoformat() if session.ended_at else None,
                    session.session_name,
                    session.device_name,
                    session.os_name,
                    int(session.sync_enabled),
                    session.status,
                    session.cloud_id,
                    int(session.synced),
                    session.id,
                ),
            )
        return session

    def save_event(self, event: Event) -> Event:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO events (id, session_id, timestamp, event_type, app_name, window_title,
                                               metadata, synced, cloud_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.session_id,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    event.app_name,
                    event.window_title,
                    json.dumps(event.metadata),
                    int(event.synced),
                    event.cloud_id,
                    event.created_at.isoformat(),
                ),
            )
        return event

    def save_screenshot(self, screenshot: ScreenshotRecord) -> ScreenshotRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO screenshots (id, session_id, event_id, local_path, storage_path, ocr_text,
                                                    captured_at, synced, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    screenshot.id,
                    screenshot.session_id,
                    screenshot.event_id,
                    screenshot.local_path,
                    screenshot.storage_path,
                    screenshot.ocr_text,
                    screenshot.captured_at.isoformat(),
                    int(screenshot.synced),
                    screenshot.created_at.isoformat(),
                ),
            )
        return screenshot

    def save_summary(self, summary: Summary) -> Summary:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO summaries (id, session_id, pseudocode, suggestions, synced, cloud_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary.id,
                    summary.session_id,
                    summary.pseudocode,
                    json.dumps(summary.suggestions),
                    int(summary.synced),
                    summary.cloud_id,
                    summary.created_at.isoformat(),
                ),
            )
        return summary

    def get_latest_session(self) -> Session | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions ORDER BY started_at DESC LIMIT 1"
            ).fetchone()
        return self._row_to_session(row) if row else None

    def get_active_session(self) -> Session | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE status = 'running' ORDER BY started_at DESC LIMIT 1"
            ).fetchone()
        return self._row_to_session(row) if row else None

    def get_session(self, session_id: str) -> Session | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        return self._row_to_session(row) if row else None

    def get_events(self, session_id: str) -> list[Event]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def get_summary(self, session_id: str) -> Summary | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM summaries WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
                (session_id,),
            ).fetchone()
        return self._row_to_summary(row) if row else None

    def get_screenshots(self, session_id: str) -> list[ScreenshotRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM screenshots WHERE session_id = ? ORDER BY captured_at ASC",
                (session_id,),
            ).fetchall()
        return [self._row_to_screenshot(row) for row in rows]

    def list_unsynced_sessions(self) -> list[Session]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM sessions WHERE synced = 0").fetchall()
        return [self._row_to_session(row) for row in rows]

    def list_unsynced_events(self, session_id: str) -> list[Event]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE session_id = ? AND synced = 0 ORDER BY timestamp ASC",
                (session_id,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def list_unsynced_screenshots(self, session_id: str) -> list[ScreenshotRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM screenshots WHERE session_id = ? AND synced = 0 ORDER BY captured_at ASC",
                (session_id,),
            ).fetchall()
        return [self._row_to_screenshot(row) for row in rows]

    def list_unsynced_summaries(self, session_id: str) -> list[Summary]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM summaries WHERE session_id = ? AND synced = 0 ORDER BY created_at ASC",
                (session_id,),
            ).fetchall()
        return [self._row_to_summary(row) for row in rows]

    def mark_session_synced(self, session_id: str, cloud_id: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET synced = 1, cloud_id = COALESCE(?, cloud_id) WHERE id = ?",
                (cloud_id, session_id),
            )

    def mark_event_synced(self, event_id: str, cloud_id: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE events SET synced = 1, cloud_id = COALESCE(?, cloud_id) WHERE id = ?",
                (cloud_id, event_id),
            )

    def mark_screenshot_synced(self, screenshot_id: str, storage_path: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE screenshots SET synced = 1, storage_path = COALESCE(?, storage_path) WHERE id = ?",
                (storage_path, screenshot_id),
            )

    def mark_summary_synced(self, summary_id: str, cloud_id: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE summaries SET synced = 1, cloud_id = COALESCE(?, cloud_id) WHERE id = ?",
                (cloud_id, summary_id),
            )

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        return Session(
            id=row["id"],
            user_id=row["user_id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            session_name=row["session_name"],
            device_name=row["device_name"],
            os_name=row["os_name"],
            sync_enabled=bool(row["sync_enabled"]),
            status=row["status"],
            cloud_id=row["cloud_id"],
            synced=bool(row["synced"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _row_to_event(self, row: sqlite3.Row) -> Event:
        return Event(
            id=row["id"],
            session_id=row["session_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            event_type=EventType(row["event_type"]),
            app_name=row["app_name"],
            window_title=row["window_title"],
            metadata=json.loads(row["metadata"]),
            synced=bool(row["synced"]),
            cloud_id=row["cloud_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _row_to_screenshot(self, row: sqlite3.Row) -> ScreenshotRecord:
        return ScreenshotRecord(
            id=row["id"],
            session_id=row["session_id"],
            event_id=row["event_id"],
            local_path=row["local_path"],
            storage_path=row["storage_path"],
            ocr_text=row["ocr_text"],
            captured_at=datetime.fromisoformat(row["captured_at"]),
            synced=bool(row["synced"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _row_to_summary(self, row: sqlite3.Row) -> Summary:
        return Summary(
            id=row["id"],
            session_id=row["session_id"],
            pseudocode=row["pseudocode"],
            suggestions=json.loads(row["suggestions"]),
            synced=bool(row["synced"]),
            cloud_id=row["cloud_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
