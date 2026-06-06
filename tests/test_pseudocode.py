from datetime import datetime, timezone

from tracker.events import Event, EventType
from tracker.pseudocode import PseudocodeGenerator


def test_pseudocode_generation_from_events() -> None:
    now = datetime.now(timezone.utc)
    events = [
        Event(
            session_id="session-1",
            event_type=EventType.SESSION_START,
            timestamp=now,
            app_name="Microsoft Excel",
        ),
        Event(
            session_id="session-1",
            event_type=EventType.ACTIVE_WINDOW,
            timestamp=now,
            window_title="Budget Workbook",
        ),
        Event(
            session_id="session-1",
            event_type=EventType.MOUSE_CLICK,
            timestamp=now,
            window_title="Budget Workbook",
            metadata={"button": "left"},
        ),
        Event(
            session_id="session-1",
            event_type=EventType.KEYBOARD_SHORTCUT,
            timestamp=now,
            metadata={"shortcut": "cmd+c"},
        ),
    ]

    pseudocode = PseudocodeGenerator().generate(events)

    assert "User opened Microsoft Excel." in pseudocode
    assert 'Switched to window "Budget Workbook".' in pseudocode
    assert "User used shortcut cmd+c." in pseudocode
