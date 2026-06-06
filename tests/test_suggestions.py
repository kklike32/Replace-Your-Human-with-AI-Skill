from datetime import datetime, timezone

from tracker.events import Event, EventType
from tracker.suggestions import SuggestionEngine


def test_suggestion_engine_generates_expected_hints() -> None:
    now = datetime.now(timezone.utc)
    events = [
        Event(session_id="session-1", event_type=EventType.MOUSE_CLICK, timestamp=now)
        for _ in range(12)
    ]
    events.append(
        Event(
            session_id="session-1",
            event_type=EventType.OCR_TEXT,
            timestamp=now,
            metadata={"text": "created chart from table"},
        )
    )

    suggestions = SuggestionEngine().suggest(events, "1. User clicked left.")

    assert any("repetitive" in text.lower() for text in suggestions)
    assert any("pandas" in text.lower() for text in suggestions)
