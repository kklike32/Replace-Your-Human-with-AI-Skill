from __future__ import annotations

from tracker.events import ChunkSummary, FinalPseudocode
from tracker.llm.base import LLMClient


def generate_final_pseudocode(
    client: LLMClient,
    summaries: list[ChunkSummary],
) -> FinalPseudocode:
    ordered = sorted(summaries, key=lambda summary: summary.chunk_index)
    return client.generate_final_pseudocode(ordered)
