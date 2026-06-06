from __future__ import annotations

from tracker.events import FinalPseudocode, WorkflowInsight, WorkflowTemplate


class WorkflowTemplateGenerator:
    def generate(
        self,
        final_pseudocode: FinalPseudocode,
        workflow_insight: WorkflowInsight,
    ) -> WorkflowTemplate:
        title = self._title(final_pseudocode, workflow_insight)
        description = self._description(workflow_insight)
        return WorkflowTemplate(
            session_id=final_pseudocode.session_id,
            title=title,
            description=description,
            category=workflow_insight.detected_task_type,
            tags=workflow_insight.tags,
            pseudocode=final_pseudocode.pseudocode,
            plain_text=final_pseudocode.plain_text,
        )

    def _title(self, final_pseudocode: FinalPseudocode, workflow_insight: WorkflowInsight) -> str:
        corpus = f"{workflow_insight.summary} {final_pseudocode.plain_text}".lower()
        if "chart" in corpus and any(keyword in corpus for keyword in {"spreadsheet", "excel", "sheet", "table"}):
            return "Create Chart from Spreadsheet Table"
        if "report" in corpus and any(keyword in corpus for keyword in {"spreadsheet", "excel", "sheet"}):
            return "Generate Report from Spreadsheet Workflow"
        if final_pseudocode.pseudocode:
            first_step = final_pseudocode.pseudocode[0]
            cleaned = first_step.replace("Step 1.", "").strip(" .")
            if cleaned:
                return cleaned[:80]
        return workflow_insight.detected_task_type.replace("_", " ").title()

    def _description(self, workflow_insight: WorkflowInsight) -> str:
        return (
            f"A reusable workflow for {workflow_insight.detected_task_type.replace('_', ' ')}. "
            f"{workflow_insight.summary}"
        )
