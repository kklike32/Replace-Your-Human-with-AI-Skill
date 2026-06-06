import pytest

from tracker.storage.insforge_client import InsForgeClient


class _DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload
        self.content = b"{}"

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_insforge_client_summary_only_payloads(monkeypatch):
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append(("POST", url, json, headers, timeout))
        return _DummyResponse({"id": "server-id"})

    client = InsForgeClient("https://api.example.com", "test-key", "token")
    monkeypatch.setattr("tracker.storage.insforge_client.requests.post", fake_post)

    session_payload = {
        "id": "session-1",
        "user_id": None,
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": None,
        "session_name": None,
        "device_name": "machine",
        "os_name": "Darwin",
    }
    summary_payload = {
        "id": "summary-1",
        "session_id": "session-1",
        "chunk_index": 0,
        "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": "2026-01-01T00:00:06+00:00",
        "summary": "Reviewed a browser page.",
        "observed_apps": ["Chrome"],
        "confidence": "high",
    }
    final_payload = {
        "id": "final-1",
        "session_id": "session-1",
        "pseudocode": ["Step 1. Review the page."],
        "plain_text": "1. Review the page.",
        "suggestions": ["Pin the document."],
    }

    client.create_session(session_payload)
    client.upload_chunk_summary(summary_payload)
    client.upload_final_pseudocode(final_payload)

    assert calls[0][1].endswith("/api/database/records/sessions")
    assert calls[1][1].endswith("/api/database/records/chunk_summaries")
    assert calls[2][1].endswith("/api/database/records/final_pseudocode")
    assert calls[1][2] == summary_payload
    assert calls[2][2] == final_payload


def test_insforge_client_rejects_raw_activity_payloads():
    client = InsForgeClient("https://api.example.com", "test-key", "token")

    with pytest.raises(ValueError):
        client.upload_chunk_summary(
            {
                "id": "summary-1",
                "session_id": "session-1",
                "chunk_index": 0,
                "started_at": "2026-01-01T00:00:00+00:00",
                "ended_at": "2026-01-01T00:00:06+00:00",
                "summary": "Reviewed a browser page.",
                "observed_apps": ["Chrome"],
                "confidence": "high",
                "ocr_text": ["secret"],
            }
        )
