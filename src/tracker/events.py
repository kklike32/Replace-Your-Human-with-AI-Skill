from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(StrEnum):
    SESSION_START = "session_start"
    SESSION_STOP = "session_stop"
    MOUSE_CLICK = "mouse_click"
    KEYBOARD_KEY = "keyboard_key"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    ACTIVE_WINDOW = "active_window"
    SCREENSHOT = "screenshot"
    OCR_TEXT = "ocr_text"
    PSEUDOCODE_GENERATED = "pseudocode_generated"
    SUGGESTION_GENERATED = "suggestion_generated"


def _uuid() -> str:
    return str(uuid4())


class Session(BaseModel):
    id: str = Field(default_factory=_uuid)
    user_id: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = None
    session_name: str | None = None
    device_name: str | None = None
    os_name: str | None = None
    sync_enabled: bool = False
    status: str = "running"
    cloud_id: str | None = None
    synced: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Event(BaseModel):
    id: str = Field(default_factory=_uuid)
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: EventType
    app_name: str | None = None
    window_title: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    synced: bool = False
    cloud_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScreenshotRecord(BaseModel):
    id: str = Field(default_factory=_uuid)
    session_id: str
    event_id: str | None = None
    local_path: str
    storage_path: str | None = None
    ocr_text: str | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    synced: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Summary(BaseModel):
    id: str = Field(default_factory=_uuid)
    session_id: str
    pseudocode: str
    suggestions: list[str]
    synced: bool = False
    cloud_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
