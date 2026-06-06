from __future__ import annotations


class ActionAgent:
    """
    Future implementation.

    This agent may perform actions on the user's behalf, but only after:
    1. The user explicitly approves the action.
    2. The action is previewed in plain English.
    3. The system confirms the target app/window.
    4. The action is logged.
    """

    # TODO: Add explicit approval workflow before any action execution.
    def run(self) -> None:
        raise NotImplementedError("ActionAgent is a future placeholder.")
