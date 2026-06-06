from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import requests


class InsForgeClient:
    def __init__(self, base_url: str, api_key: str, auth_token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.auth_token = auth_token

    def _headers(self, content_type: str = "application/json") -> dict[str, str]:
        headers = {"x-api-key": self.api_key}
        if content_type:
            headers["Content-Type"] = content_type
        # For admin flows, InsForge accepts the project API key as a bearer token.
        bearer = self.auth_token or self.api_key
        if bearer:
            headers["Authorization"] = f"Bearer {bearer}"
        return headers

    def create_session(self, payload: dict) -> dict:
        return self._insert_record("sessions", payload)

    def insert_event(self, payload: dict) -> dict:
        return self._insert_record("events", payload)

    def upload_screenshot(self, local_path: str, storage_path: str, bucket: str) -> dict:
        file_path = Path(local_path)
        strategy_response = requests.post(
            f"{self.base_url}/api/storage/buckets/{bucket}/upload-strategy",
            json={
                "filename": storage_path,
                "contentType": "image/png",
                "size": file_path.stat().st_size,
            },
            headers=self._headers(),
            timeout=30,
        )
        strategy_response.raise_for_status()
        strategy = strategy_response.json() if strategy_response.content else {}

        method = strategy.get("method")
        if method == "presigned":
            upload_url = strategy.get("uploadUrl")
            if not upload_url:
                raise ValueError("InsForge upload strategy missing uploadUrl")

            multipart_fields = {
                key: (None, value) for key, value in strategy.get("fields", {}).items()
            }
            with file_path.open("rb") as file_handle:
                multipart_fields["file"] = (file_path.name, file_handle, "image/png")
                upload_response = requests.post(
                    upload_url,
                    files=multipart_fields,
                    timeout=60,
                )
            upload_response.raise_for_status()

            if strategy.get("confirmRequired") and strategy.get("confirmUrl"):
                confirm_url = str(strategy["confirmUrl"])
                if confirm_url.startswith("http://") or confirm_url.startswith("https://"):
                    final_url = confirm_url
                else:
                    final_url = f"{self.base_url}{confirm_url}"

                confirm_response = requests.post(
                    final_url,
                    json={
                        "size": file_path.stat().st_size,
                        "contentType": "image/png",
                    },
                    headers=self._headers(),
                    timeout=30,
                )
                confirm_response.raise_for_status()
                if confirm_response.content:
                    return confirm_response.json()

            return {
                "ok": True,
                "path": storage_path,
                "bucket": bucket,
            }

        # Fallback for backends that expose direct object uploads.
        encoded_path = quote(storage_path, safe="/")
        with file_path.open("rb") as file_handle:
            response = requests.put(
                f"{self.base_url}/api/storage/buckets/{bucket}/objects/{encoded_path}",
                files={"file": (file_path.name, file_handle, "image/png")},
                headers=self._headers(content_type=""),
                timeout=60,
            )
        response.raise_for_status()
        return response.json() if response.content else {"ok": True, "path": storage_path}

    def save_summary(self, payload: dict) -> dict:
        return self._insert_record("summaries", payload)

    def _insert_record(self, table: str, payload: dict) -> dict:
        return self._post_json(
            f"/api/database/records/{table}",
            payload,
            extra_headers={"Prefer": "return=representation"},
        )

    def _post_json(
        self,
        route: str,
        payload: dict,
        extra_headers: dict[str, str] | None = None,
    ) -> dict:
        headers = self._headers()
        if extra_headers:
            headers.update(extra_headers)
        response = requests.post(
            f"{self.base_url}{route}",
            json=payload,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        parsed = response.json()
        if isinstance(parsed, list):
            if not parsed:
                return {}
            first = parsed[0]
            return first if isinstance(first, dict) else {}
        return parsed if isinstance(parsed, dict) else {}
