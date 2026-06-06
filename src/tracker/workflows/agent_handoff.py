from __future__ import annotations

from tracker.events import AgentHandoffDraft, FinalPseudocode, WorkflowTemplate


class AgentHandoffPlanner:
    def create_draft(
        self,
        workflow_template: WorkflowTemplate | None,
        final_pseudocode: FinalPseudocode,
        automation_score: int,
    ) -> AgentHandoffDraft:
        title = workflow_template.title if workflow_template else "this workflow"
        category = workflow_template.category if workflow_template else "workflow"
        return AgentHandoffDraft(
            session_id=final_pseudocode.session_id,
            template_id=workflow_template.id if workflow_template else None,
            status="draft",
            proposed_action=(
                f"Turn {title} into a reusable Python or agent-assisted automation for {category}."
            ),
            action_plan=[
                "Identify the expected inputs, outputs, and preconditions.",
                "Map each pseudocode step to an explicit automation operation.",
                "Create a dry-run implementation plan before touching real files or systems.",
                "Add review checkpoints for sensitive or judgment-heavy steps.",
                f"Keep execution blocked until the user approves the plan. Current automation score: {automation_score}.",
            ],
            requires_user_approval=True,
        )
