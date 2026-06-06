from __future__ import annotations


class AutomationScorer:
    REPETITIVE_KEYWORDS = {
        "repeat",
        "repetitive",
        "copy",
        "paste",
        "export",
        "import",
        "rename",
        "save",
        "update",
        "submit",
        "fill",
        "download",
        "upload",
        "filter",
        "sort",
        "transform",
        "chart",
        "report",
        "spreadsheet",
        "excel",
        "sheet",
        "form",
        "browser",
        "admin",
        "dashboard",
        "table",
    }
    LOW_AUTOMATION_KEYWORDS = {
        "brainstorm",
        "design",
        "creative",
        "judge",
        "judgment",
        "review",
        "analyze",
        "ambiguous",
        "private",
        "confidential",
        "sensitive",
        "write",
        "draft",
    }

    def score(self, pseudocode: list[str], summaries: list[str]) -> tuple[int, str]:
        corpus = " ".join([*pseudocode, *summaries]).lower()
        repetitive_hits = sum(1 for keyword in self.REPETITIVE_KEYWORDS if keyword in corpus)
        low_automation_hits = sum(1 for keyword in self.LOW_AUTOMATION_KEYWORDS if keyword in corpus)
        sequence_bonus = min(len([step for step in pseudocode if step.strip()]) * 4, 20)

        score = 35 + repetitive_hits * 6 + sequence_bonus - low_automation_hits * 7
        score = max(0, min(100, score))

        reasons: list[str] = []
        if repetitive_hits:
            reasons.append("The workflow appears repetitive and structured.")
        if any(keyword in corpus for keyword in {"spreadsheet", "excel", "sheet", "table", "chart"}):
            reasons.append("It includes spreadsheet or reporting actions that map well to automation.")
        if any(keyword in corpus for keyword in {"form", "submit", "admin", "dashboard", "browser"}):
            reasons.append("It uses browser or form-style steps that could become a guided automation.")
        if low_automation_hits:
            reasons.append("Some steps still look judgment-heavy or sensitive, so approval should remain required.")
        if not reasons:
            reasons.append("The workflow has some repeatable structure but still needs human review.")

        return score, " ".join(reasons)
