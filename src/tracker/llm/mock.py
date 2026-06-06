from __future__ import annotations

from collections import Counter

from tracker.events import ActivityChunk, ChunkSummary, FinalPseudocode

from .base import LLMClient


class MockLLMClient(LLMClient):
    def summarize_chunk(self, chunk: ActivityChunk) -> ChunkSummary:
        apps = [entry.get("app_name") for entry in chunk.active_windows if entry.get("app_name")]
        observed_apps = sorted(dict.fromkeys(apps))
        screenshot_count = len(chunk.screenshots)
        click_count = len(chunk.mouse_events)
        shortcut_count = len(chunk.keyboard_shortcuts)
        text_count = len([text for text in chunk.ocr_text if text.strip()])
        app_text = ", ".join(observed_apps) if observed_apps else "an unknown app"
        summary = (
            f"Chunk {chunk.chunk_index}: Observed {app_text}; "
            f"{screenshot_count} screenshots, {click_count} mouse events, "
            f"{shortcut_count} shortcuts, {text_count} OCR snippets."
        )
        confidence = "high" if observed_apps or screenshot_count else "medium"
        return ChunkSummary(
            session_id=chunk.session_id,
            chunk_index=chunk.chunk_index,
            started_at=chunk.started_at,
            ended_at=chunk.ended_at,
            summary=summary,
            observed_apps=observed_apps,
            confidence=confidence,
        )

    def generate_final_pseudocode(self, summaries: list[ChunkSummary]) -> FinalPseudocode:
        if not summaries:
            steps = ["Step 1. No activity summaries were available."]
            plain_text = "1. No activity summaries were available."
            suggestions = ["Capture a longer session before generating a final workflow."]
            return FinalPseudocode(
                session_id="unknown",
                pseudocode=steps,
                plain_text=plain_text,
                suggestions=suggestions,
            )

        ordered = sorted(summaries, key=lambda summary: summary.chunk_index)
        app_counter = Counter(
            app
            for summary in ordered
            for app in summary.observed_apps
        )
        dominant_apps = ", ".join(app for app, _ in app_counter.most_common(3)) or "multiple apps"

        steps = [
            f"Step {index}. {summary.summary}"
            for index, summary in enumerate(ordered, start=1)
        ]
        suggestions = [
            f"Consider automating repeated work in {dominant_apps}."
            if app_counter
            else "Review the summaries and add provider-specific prompt tuning."
        ]
        plain_text = "\n".join(
            f"{index}. {summary.summary}" for index, summary in enumerate(ordered, start=1)
        )
        return FinalPseudocode(
            session_id=ordered[0].session_id,
            pseudocode=steps,
            plain_text=plain_text,
            suggestions=suggestions,
        )
