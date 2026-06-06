from __future__ import annotations

from abc import ABC, abstractmethod

from tracker.events import ChunkSummary, Event, FinalPseudocode, ScreenshotRecord, Session


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
