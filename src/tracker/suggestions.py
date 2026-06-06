from __future__ import annotations

from .events import Event, EventType


class SuggestionEngine:
    def suggest(self, events: list[Event], pseudocode: str) -> list[str]:
        suggestions: list[str] = []

        click_count = sum(1 for event in events if event.event_type == EventType.MOUSE_CLICK)
        shortcut_count = sum(
            1 for event in events if event.event_type == EventType.KEYBOARD_SHORTCUT
        )
        ocr_texts = [
            str(event.metadata.get("text", "")).lower()
            for event in events
            if event.event_type == EventType.OCR_TEXT
        ]

        if click_count >= 10:
            suggestions.append(
                "This workflow appears repetitive. Consider turning it into a Python script."
            )

        if any("chart" in text or "table" in text for text in ocr_texts):
            suggestions.append(
                "The session involved spreadsheet operations. Consider generating a pandas workflow."
            )

        if shortcut_count >= 3:
            suggestions.append(
                "You used repeated shortcuts. A lightweight task script could reduce context switching."
            )

        if "No significant actions captured" in pseudocode:
            suggestions.append(
                "Capture a longer session or lower screenshot interval to improve summary quality."
            )
        else:
            suggestions.append(
                "The user created or edited visual output. Consider saving this as a reusable reporting template."
            )

        return suggestions
