from pathlib import Path

from tracker.events import ActivityChunk, ChunkSummary
from tracker.llm.mock import MockLLMClient


def test_mock_llm_chunk_summary_generation() -> None:
    client = MockLLMClient()
    chunk = ActivityChunk(
        session_id="session-1",
        chunk_index=2,
        started_at="2026-01-01T00:00:00+00:00",
        ended_at="2026-01-01T00:00:06+00:00",
        screenshots=[Path("/tmp/one.png"), Path("/tmp/two.png"), Path("/tmp/three.png")],
        mouse_events=[{"button": "left"}],
        keyboard_shortcuts=[{"shortcut": "cmd+c"}],
        active_windows=[{"app_name": "Chrome", "window_title": "Docs"}],
        ocr_text=["Project notes"],
    )

    summary = client.summarize_chunk(chunk)

    assert summary.chunk_index == 2
    assert summary.observed_apps == ["Chrome"]
    assert "3 screenshots" in summary.summary


def test_mock_llm_final_pseudocode_generation() -> None:
    client = MockLLMClient()
    summaries = [
        ChunkSummary(
            session_id="session-1",
            chunk_index=0,
            started_at="2026-01-01T00:00:00+00:00",
            ended_at="2026-01-01T00:00:06+00:00",
            summary="Opened Chrome and read documentation.",
            observed_apps=["Chrome"],
            confidence="high",
        ),
        ChunkSummary(
            session_id="session-1",
            chunk_index=1,
            started_at="2026-01-01T00:00:06+00:00",
            ended_at="2026-01-01T00:00:12+00:00",
            summary="Copied a command and switched to Terminal.",
            observed_apps=["Chrome", "Terminal"],
            confidence="high",
        ),
    ]

    final = client.generate_final_pseudocode(summaries)

    assert final.session_id == "session-1"
    assert len(final.pseudocode) == 2
    assert "Opened Chrome" in final.plain_text
    assert final.suggestions
