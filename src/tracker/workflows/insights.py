from __future__ import annotations

from collections import Counter

from tracker.events import ChunkSummary, FinalPseudocode, WorkflowInsight

from .automation_score import AutomationScorer


class WorkflowInsightGenerator:
    def __init__(self, scorer: AutomationScorer | None = None) -> None:
        self.scorer = scorer or AutomationScorer()

    def generate(
        self,
        final_pseudocode: FinalPseudocode,
        chunk_summaries: list[ChunkSummary],
        suggestions: list[str] | None = None,
    ) -> WorkflowInsight:
        summaries = [summary.summary for summary in chunk_summaries]
        main_apps = self._main_apps(chunk_summaries)
        task_type = self._detect_task_type(final_pseudocode, summaries, main_apps)
        automation_score, automation_reason = self.scorer.score(
            final_pseudocode.pseudocode,
            summaries,
        )
        tags = self._build_tags(task_type, main_apps, final_pseudocode, automation_score)
        summary = self._build_summary(task_type, final_pseudocode, main_apps)
        recommended_next_action = self._recommended_next_action(
            automation_score,
            task_type,
            suggestions or final_pseudocode.suggestions,
        )
        return WorkflowInsight(
            session_id=final_pseudocode.session_id,
            summary=summary,
            main_apps=main_apps,
            detected_task_type=task_type,
            tags=tags,
            automation_score=automation_score,
            automation_reason=automation_reason,
            recommended_next_action=recommended_next_action,
        )

    def _main_apps(self, chunk_summaries: list[ChunkSummary]) -> list[str]:
        counts = Counter(
            app
            for summary in chunk_summaries
            for app in summary.observed_apps
            if app and app.strip()
        )
        return [app for app, _count in counts.most_common(5)]

    def _detect_task_type(
        self,
        final_pseudocode: FinalPseudocode,
        summaries: list[str],
        main_apps: list[str],
    ) -> str:
        corpus = " ".join([final_pseudocode.plain_text, *summaries, *main_apps]).lower()
        if any(keyword in corpus for keyword in {"spreadsheet", "excel", "sheet", "table", "chart"}):
            return "spreadsheet_automation"
        if any(keyword in corpus for keyword in {"browser", "dashboard", "admin", "form"}):
            return "browser_admin_workflow"
        if any(keyword in corpus for keyword in {"report", "export", "summary"}):
            return "reporting_workflow"
        if any(keyword in corpus for keyword in {"document", "docs", "word", "write"}):
            return "document_workflow"
        return "general_workflow"

    def _build_tags(
        self,
        task_type: str,
        main_apps: list[str],
        final_pseudocode: FinalPseudocode,
        automation_score: int,
    ) -> list[str]:
        tags = {task_type}
        for app in main_apps:
            normalized = app.strip().lower().replace(" ", "_")
            if normalized:
                tags.add(normalized)
        corpus = final_pseudocode.plain_text.lower()
        keyword_tags = {
            "chart": "chart",
            "report": "reporting",
            "export": "export",
            "spreadsheet": "spreadsheet",
            "excel": "excel",
            "browser": "browser",
            "form": "forms",
            "copy": "copy_paste",
            "paste": "copy_paste",
        }
        for keyword, tag in keyword_tags.items():
            if keyword in corpus:
                tags.add(tag)
        tags.add("automation_candidate" if automation_score >= 75 else "human_review")
        return sorted(tags)

    def _build_summary(
        self,
        task_type: str,
        final_pseudocode: FinalPseudocode,
        main_apps: list[str],
    ) -> str:
        first_step = final_pseudocode.pseudocode[0] if final_pseudocode.pseudocode else final_pseudocode.plain_text
        app_text = ", ".join(main_apps[:3]) or "desktop apps"
        return (
            f"This session looks like a {task_type.replace('_', ' ')} using {app_text}. "
            f"It starts with: {first_step}"
        )

    def _recommended_next_action(
        self,
        automation_score: int,
        task_type: str,
        suggestions: list[str],
    ) -> str:
        if automation_score >= 75:
            return "Create a reusable workflow template and draft a Python automation plan."
        if suggestions:
            return suggestions[0]
        return (
            f"Review the {task_type.replace('_', ' ')} summary with a human and decide whether to "
            "turn it into a reusable template."
        )
