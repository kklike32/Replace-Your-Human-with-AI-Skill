from tracker.storage.insforge_client import InsForgeClient


class _DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload
        self.content = b"{}"

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_insforge_client_payloads(monkeypatch):
    calls = []

    def fake_post(url, json, headers, timeout):
        calls.append(("POST", url, json, headers, timeout))
        return _DummyResponse({"id": "server-id"})

    client = InsForgeClient("https://api.example.com", "test-key", "token")
    monkeypatch.setattr("tracker.storage.insforge_client.requests.post", fake_post)

    payload = {"id": "session-1", "sync_enabled": True}
    response = client.create_session(payload)

    assert response["id"] == "server-id"
    assert calls
    method, url, posted_json, headers, timeout = calls[0]
    assert method == "POST"
    assert url.endswith("/v1/sessions")
    assert posted_json == payload
    assert headers["x-api-key"] == "test-key"
    assert "Authorization" in headers
    assert timeout == 15
