"""Objective selection for Cassandra missions."""

from __future__ import annotations

from cassandra.experiments import Mission, Objective
from cassandra.planner.objective import CurrentObjective


class ObjectiveSelector:
    """Select the next objective from a mission."""

    def select(
        self,
        mission: Mission,
    ) -> CurrentObjective | None:
        """Return the highest-priority available mission objective."""

        objective = self._highest_priority(
            mission.objectives
        )

        if objective is None:
            return None

        return CurrentObjective(
            description=objective.description,
            source_objective_id=objective.objective_id,
        )

    def _highest_priority(
        self,
        objectives: list[Objective],
    ) -> Objective | None:
        """Return the highest-priority objective."""

        if not objectives:
            return None

        return min(
            objectives,
            key=lambda objective: objective.priority,
        )