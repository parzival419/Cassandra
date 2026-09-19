"""Action request construction for Cassandra."""

from __future__ import annotations

from cassandra.execution.request import ActionRequest
from cassandra.planner import Action, CurrentObjective


class ActionRequestBuilder:
    """Build execution requests from Cassandra planning state."""

    def build(
        self,
        action: Action,
        objective: CurrentObjective,
        experiment_instructions: str,
        observation: str,
    ) -> ActionRequest:
        """Build an action request from current experiment state."""

        return ActionRequest(
            action_id=action.action_id,
            instruction=action.description,
            context={
                "current_objective": objective.description,
                "experiment_instructions": experiment_instructions,
                "observation": observation,
            },
        )