from __future__ import annotations

from abc import ABC, abstractmethod

from tracker.events import ActivityChunk, ChunkSummary, FinalPseudocode


class LLMClient(ABC):
    @abstractmethod
    def summarize_chunk(self, chunk: ActivityChunk) -> ChunkSummary:
        raise NotImplementedError

    @abstractmethod
    def generate_final_pseudocode(self, summaries: list[ChunkSummary]) -> FinalPseudocode:
        raise NotImplementedError
