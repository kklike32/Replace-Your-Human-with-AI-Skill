from __future__ import annotations

from tracker.config import TrackerConfig

from .base import LLMClient
from .gemini_vertex import VertexGeminiClient
from .mock import MockLLMClient


def build_llm_client(config: TrackerConfig, provider: str | None = None) -> LLMClient:
    chosen = (provider or config.llm_provider).strip().lower()
    if chosen == "mock":
        return MockLLMClient()
    if chosen == "vertex_gemini":
        return VertexGeminiClient(config)
    raise ValueError(f"Unsupported LLM provider: {chosen}")


__all__ = ["LLMClient", "MockLLMClient", "VertexGeminiClient", "build_llm_client"]
