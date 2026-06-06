from __future__ import annotations

import requests

from tracker.config import TrackerConfig
from tracker.privacy import assert_remote_payload_allowed


class InsForgeClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        auth_token: str | None = None,
        summaries_table: str = "chunk_summaries",
        final_table: str = "final_pseudocode",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.auth_token = auth_token
        self.summaries_table = summaries_table
        self.final_table = final_table

    @classmethod
    def from_config(cls, config: TrackerConfig) -> InsForgeClient:
        return cls(
            base_url=str(config.insforge_base_url),
            api_key=str(config.insforge_api_key),
            auth_token=config.insforge_auth_token,
            summaries_table=config.insforge_summaries_table,
            final_table=config.insforge_final_table,
        )

    def _headers(self) -> dict[str, str]:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        bearer = self.auth_token or self.api_key
        if bearer:
            headers["Authorization"] = f"Bearer {bearer}"
        return headers

    def create_session(self, payload: dict) -> dict:
        assert_remote_payload_allowed("sessions", payload)
        return self._insert_record("sessions", payload)

    def upload_chunk_summary(self, payload: dict) -> dict:
        assert_remote_payload_allowed("chunk_summaries", payload)
        return self._insert_record(self.summaries_table, payload)

    def upload_final_pseudocode(self, payload: dict) -> dict:
        assert_remote_payload_allowed("final_pseudocode", payload)
        return self._insert_record(self.final_table, payload)

    def _insert_record(self, table: str, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}/api/database/records/{table}",
            json=payload,
            headers={**self._headers(), "Prefer": "return=representation"},
            timeout=15,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        parsed = response.json()
        if isinstance(parsed, list):
            return parsed[0] if parsed and isinstance(parsed[0], dict) else {}
        return parsed if isinstance(parsed, dict) else {}
