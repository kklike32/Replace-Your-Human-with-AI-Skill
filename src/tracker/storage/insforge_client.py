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
        workflow_insights_table: str = "workflow_insights",
        workflow_templates_table: str = "workflow_templates",
        agent_handoff_table: str = "agent_handoff_queue",
        workflow_search_table: str = "workflow_search_index",
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.auth_token = auth_token
        self.summaries_table = summaries_table
        self.final_table = final_table
        self.workflow_insights_table = workflow_insights_table
        self.workflow_templates_table = workflow_templates_table
        self.agent_handoff_table = agent_handoff_table
        self.workflow_search_table = workflow_search_table

    @classmethod
    def from_config(cls, config: TrackerConfig) -> InsForgeClient:
        return cls(
            base_url=str(config.insforge_base_url),
            api_key=str(config.insforge_api_key),
            auth_token=config.insforge_auth_token,
            summaries_table=config.insforge_summaries_table,
            final_table=config.insforge_final_table,
            workflow_insights_table=config.insforge_workflow_insights_table,
            workflow_templates_table=config.insforge_workflow_templates_table,
            agent_handoff_table=config.insforge_agent_handoff_table,
            workflow_search_table=config.insforge_workflow_search_table,
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

    def upload_workflow_insight(self, payload: dict) -> dict:
        assert_remote_payload_allowed("workflow_insights", payload)
        return self._insert_record(self.workflow_insights_table, payload)

    def upload_workflow_template(self, payload: dict) -> dict:
        assert_remote_payload_allowed("workflow_templates", payload)
        return self._insert_record(self.workflow_templates_table, payload)

    def upload_agent_handoff_draft(self, payload: dict) -> dict:
        assert_remote_payload_allowed("agent_handoff_queue", payload)
        return self._insert_record(self.agent_handoff_table, payload)

    def upload_search_index_record(self, payload: dict) -> dict:
        assert_remote_payload_allowed("workflow_search_index", payload)
        return self._insert_record(self.workflow_search_table, payload)

    def search_workflows(self, query: str, limit: int = 10) -> list[dict]:
        records = self._list_records(
            self.workflow_search_table,
            {"limit": limit, "query": query},
        )
        normalized_query = query.lower()
        return [
            record
            for record in records
            if normalized_query in str(record.get("searchable_text", "")).lower()
        ][:limit]

    def list_workflow_templates(self, limit: int = 10) -> list[dict]:
        return self._list_records(
            self.workflow_templates_table,
            {"limit": limit, "order_by": "created_at", "order": "desc"},
        )

    def list_workflow_insights(self, session_id: str | None = None, limit: int = 10) -> list[dict]:
        params = {"limit": limit, "order_by": "created_at", "order": "desc"}
        if session_id:
            params["session_id"] = session_id
        return self._list_records(self.workflow_insights_table, params)

    def get_workflow_template(self, workflow_id: str) -> dict:
        return self._get_record(self.workflow_templates_table, workflow_id)

    def get_agent_handoff(self, session_id: str) -> list[dict]:
        return self._list_records(
            self.agent_handoff_table,
            {"session_id": session_id, "limit": 10, "order_by": "created_at", "order": "desc"},
        )

    def list_final_pseudocode(self, session_id: str) -> list[dict]:
        return self._list_records(
            self.final_table,
            {"session_id": session_id, "limit": 10, "order_by": "created_at", "order": "desc"},
        )

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

    def _list_records(self, table: str, params: dict[str, object] | None = None) -> list[dict]:
        response = requests.get(
            f"{self.base_url}/api/database/records/{table}",
            params=params or {},
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        if not response.content:
            return []
        parsed = response.json()
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            items = parsed.get("data")
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return []

    def _get_record(self, table: str, record_id: str) -> dict:
        response = requests.get(
            f"{self.base_url}/api/database/records/{table}/{record_id}",
            headers=self._headers(),
            timeout=15,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        parsed = response.json()
        return parsed if isinstance(parsed, dict) else {}
