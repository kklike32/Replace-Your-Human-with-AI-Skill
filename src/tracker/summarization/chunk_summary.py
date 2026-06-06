from __future__ import annotations

from tracker.events import ActivityChunk, ChunkSummary
from tracker.llm.base import LLMClient
from tracker.privacy import redact_text


def summarize_activity_chunk(client: LLMClient, chunk: ActivityChunk) -> ChunkSummary:
    sanitized_chunk = ActivityChunk(
        session_id=chunk.session_id,
        chunk_index=chunk.chunk_index,
        started_at=chunk.started_at,
        ended_at=chunk.ended_at,
        screenshots=list(chunk.screenshots),
        mouse_events=[
            {
                "timestamp": event.get("timestamp"),
                "button": event.get("button"),
            }
            for event in chunk.mouse_events
        ],
        keyboard_shortcuts=[dict(shortcut) for shortcut in chunk.keyboard_shortcuts],
        active_windows=[
            {
                "app_name": item.get("app_name"),
                "window_title": redact_text(str(item.get("window_title") or ""), max_len=120),
                "timestamp": item.get("timestamp"),
            }
            for item in chunk.active_windows
        ],
        ocr_text=[redact_text(text, max_len=200) for text in chunk.ocr_text if text.strip()],
    )
    return client.summarize_chunk(sanitized_chunk)
