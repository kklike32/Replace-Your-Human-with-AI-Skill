from __future__ import annotations

from tracker.config import TrackerConfig
from tracker.storage.insforge_client import InsForgeClient
from tracker.storage.local_sqlite import LocalSQLiteRepository


class SyncService:
    def __init__(
        self,
        repository: LocalSQLiteRepository,
        client: InsForgeClient,
        config: TrackerConfig,
    ) -> None:
        self.repository = repository
        self.client = client
        self.config = config

    def sync_all(self) -> dict[str, int]:
        synced_sessions = 0
        synced_chunk_summaries = 0
        synced_final_pseudocode = 0

        for session in self.repository.list_unsynced_sessions():
            created = self.client.create_session(
                {
                    "id": session.id,
                    "user_id": session.user_id,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                    "session_name": session.session_name,
                    "device_name": session.device_name,
                    "os_name": session.os_name,
                }
            )
            self.repository.mark_session_synced(session.id, created.get("id"))
            synced_sessions += 1

        for summary in self.repository.list_unsynced_chunk_summaries():
            created_summary = self.client.upload_chunk_summary(
                {
                    "id": summary.id,
                    "session_id": summary.session_id,
                    "chunk_index": summary.chunk_index,
                    "started_at": summary.started_at,
                    "ended_at": summary.ended_at,
                    "summary": summary.summary,
                    "observed_apps": summary.observed_apps,
                    "confidence": summary.confidence,
                }
            )
            self.repository.mark_chunk_summary_synced(summary.id, created_summary.get("id"))
            synced_chunk_summaries += 1

        for final in self.repository.list_unsynced_final_pseudocode():
            created_final = self.client.upload_final_pseudocode(
                {
                    "id": final.id,
                    "session_id": final.session_id,
                    "pseudocode": final.pseudocode,
                    "plain_text": final.plain_text,
                    "suggestions": final.suggestions,
                }
            )
            self.repository.mark_final_pseudocode_synced(final.id, created_final.get("id"))
            synced_final_pseudocode += 1

        return {
            "sessions": synced_sessions,
            "chunk_summaries": synced_chunk_summaries,
            "final_pseudocode": synced_final_pseudocode,
        }

    def sync_session(self, session_id: str) -> dict[str, int]:
        synced_chunk_summaries = 0
        synced_final_pseudocode = 0

        session = self.repository.get_session(session_id)
        if session and not session.synced:
            created = self.client.create_session(
                {
                    "id": session.id,
                    "user_id": session.user_id,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                    "session_name": session.session_name,
                    "device_name": session.device_name,
                    "os_name": session.os_name,
                }
            )
            self.repository.mark_session_synced(session.id, created.get("id"))

        for summary in self.repository.list_unsynced_chunk_summaries(session_id):
            created_summary = self.client.upload_chunk_summary(
                {
                    "id": summary.id,
                    "session_id": summary.session_id,
                    "chunk_index": summary.chunk_index,
                    "started_at": summary.started_at,
                    "ended_at": summary.ended_at,
                    "summary": summary.summary,
                    "observed_apps": summary.observed_apps,
                    "confidence": summary.confidence,
                }
            )
            self.repository.mark_chunk_summary_synced(summary.id, created_summary.get("id"))
            synced_chunk_summaries += 1

        for final in self.repository.list_unsynced_final_pseudocode(session_id):
            created_final = self.client.upload_final_pseudocode(
                {
                    "id": final.id,
                    "session_id": final.session_id,
                    "pseudocode": final.pseudocode,
                    "plain_text": final.plain_text,
                    "suggestions": final.suggestions,
                }
            )
            self.repository.mark_final_pseudocode_synced(final.id, created_final.get("id"))
            synced_final_pseudocode += 1

        return {
            "chunk_summaries": synced_chunk_summaries,
            "final_pseudocode": synced_final_pseudocode,
        }
