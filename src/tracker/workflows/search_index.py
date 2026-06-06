from __future__ import annotations

from tracker.events import FinalPseudocode, WorkflowInsight, WorkflowSearchIndexRecord, WorkflowTemplate


class WorkflowSearchIndexBuilder:
    def build(
        self,
        final_pseudocode: FinalPseudocode,
        workflow_insight: WorkflowInsight,
        workflow_template: WorkflowTemplate | None,
    ) -> WorkflowSearchIndexRecord:
        title = workflow_template.title if workflow_template else workflow_insight.detected_task_type
        category = (
            workflow_template.category if workflow_template else workflow_insight.detected_task_type
        )
        tag_text = " ".join(workflow_template.tags if workflow_template else workflow_insight.tags)
        searchable_text = " ".join(
            part
            for part in [
                title,
                category,
                tag_text,
                final_pseudocode.plain_text,
                workflow_insight.summary,
                workflow_insight.recommended_next_action,
            ]
            if part
        )
        return WorkflowSearchIndexRecord(
            session_id=final_pseudocode.session_id,
            template_id=workflow_template.id if workflow_template else None,
            searchable_text=searchable_text,
            tags=workflow_template.tags if workflow_template else workflow_insight.tags,
        )
