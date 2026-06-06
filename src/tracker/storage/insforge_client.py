from __future__ import annotations

from pathlib import Path

import requests


class InsForgeClient:
    def __init__(self, base_url: str, api_key: str, auth_token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.auth_token = auth_token

    def _headers(self, content_type: str = "application/json") -> dict[str, str]:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": content_type,
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def create_session(self, payload: dict) -> dict:
        return self._post_json("/v1/sessions", payload)

    def insert_event(self, payload: dict) -> dict:
        return self._post_json("/v1/events", payload)

    def upload_screenshot(self, local_path: str, storage_path: str, bucket: str) -> dict:
        with Path(local_path).open("rb") as file_handle:
            response = requests.put(
                f"{self.base_url}/v1/storage/{bucket}/{storage_path}",
                data=file_handle,
                headers=self._headers(content_type="image/png"),
                timeout=15,
            )
        response.raise_for_status()
        return response.json() if response.content else {"ok": True, "path": storage_path}

    def save_summary(self, payload: dict) -> dict:
        return self._post_json("/v1/summaries", payload)

    def _post_json(self, route: str, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}{route}",
            json=payload,
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        return response.json() if response.content else {}
