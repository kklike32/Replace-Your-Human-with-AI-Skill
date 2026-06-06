from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from tracker.events import (
    AgentHandoffDraft,
    ChunkSummary,
    Event,
    FinalPseudocode,
    ScreenshotRecord,
    Session,
    WorkflowInsight,
    WorkflowSearchIndexRecord,
    WorkflowTemplate,
)


class TrackerRepository(ABC):
    @abstractmethod
    def create_session(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    def update_session(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    def save_event(self, event: Event) -> Event:
        raise NotImplementedError

    @abstractmethod
    def save_screenshot(self, screenshot: ScreenshotRecord) -> ScreenshotRecord:
        raise NotImplementedError

    @abstractmethod
    def save_chunk_summary(self, summary: ChunkSummary) -> ChunkSummary:
        raise NotImplementedError

    @abstractmethod
    def save_final_pseudocode(self, final: FinalPseudocode) -> FinalPseudocode:
        raise NotImplementedError

    @abstractmethod
    def save_workflow_insight(self, insight: WorkflowInsight) -> WorkflowInsight:
        raise NotImplementedError

    @abstractmethod
    def save_workflow_template(self, template: WorkflowTemplate) -> WorkflowTemplate:
        raise NotImplementedError

    @abstractmethod
    def save_agent_handoff_draft(self, draft: AgentHandoffDraft) -> AgentHandoffDraft:
        raise NotImplementedError

    @abstractmethod
    def save_workflow_search_index(
        self,
        record: WorkflowSearchIndexRecord,
    ) -> WorkflowSearchIndexRecord:
        raise NotImplementedError

    @abstractmethod
    def purge_expired_raw_data(self, session_id: str, cutoff: datetime) -> dict[str, int]:
        raise NotImplementedError
