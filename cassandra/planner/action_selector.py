"""Action selection for Cassandra plans."""

from __future__ import annotations

from cassandra.planner.action import Action
from cassandra.planner.plan import Plan


class ActionSelector:
    """Select the next pending action from a plan."""

    def select(
        self,
        plan: Plan,
    ) -> Action | None:
        """Return the first pending action in plan order."""

        for action in plan.actions:
            if action.status == "pending":
                return action

        return None