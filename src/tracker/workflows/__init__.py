from __future__ import annotations

from dataclasses import dataclass

from tracker.events import (
    AgentHandoffDraft,
    ChunkSummary,
    FinalPseudocode,
    WorkflowInsight,
    WorkflowSearchIndexRecord,
    WorkflowTemplate,
)

from .agent_handoff import AgentHandoffPlanner
from .automation_score import AutomationScorer
from .insights import WorkflowInsightGenerator
from .search_index import WorkflowSearchIndexBuilder
from .templates import WorkflowTemplateGenerator


@dataclass(slots=True)
class WorkflowArtifacts:
    insight: WorkflowInsight
    template: WorkflowTemplate | None
    search_index: WorkflowSearchIndexRecord
    handoff_draft: AgentHandoffDraft | None


def build_workflow_artifacts(
    final_pseudocode: FinalPseudocode,
    chunk_summaries: list[ChunkSummary],
    enable_template_creation: bool = True,
    enable_agent_handoff_drafts: bool = True,
    handoff_threshold: int = 75,
) -> WorkflowArtifacts:
    insight = WorkflowInsightGenerator().generate(final_pseudocode, chunk_summaries)
    template = None
    if enable_template_creation:
        template = WorkflowTemplateGenerator().generate(final_pseudocode, insight)
    search_index = WorkflowSearchIndexBuilder().build(final_pseudocode, insight, template)
    handoff_draft = None
    if enable_agent_handoff_drafts and insight.automation_score >= handoff_threshold:
        handoff_draft = AgentHandoffPlanner().create_draft(
            template,
            final_pseudocode,
            insight.automation_score,
        )
    return WorkflowArtifacts(
        insight=insight,
        template=template,
        search_index=search_index,
        handoff_draft=handoff_draft,
    )


__all__ = [
    "AgentHandoffDraft",
    "AgentHandoffPlanner",
    "AutomationScorer",
    "WorkflowArtifacts",
    "WorkflowInsight",
    "WorkflowInsightGenerator",
    "WorkflowSearchIndexBuilder",
    "WorkflowSearchIndexRecord",
    "WorkflowTemplate",
    "WorkflowTemplateGenerator",
    "build_workflow_artifacts",
]
