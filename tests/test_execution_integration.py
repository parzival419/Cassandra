"""Integration tests for Cassandra execution flow."""

from __future__ import annotations

import unittest

from cassandra.execution import (
    ActionRequestBuilder,
    DeterministicExecutor,
)
from cassandra.planner import Action, CurrentObjective


class ExecutionIntegrationTests(unittest.TestCase):
    """Verify planning state can flow through execution."""

    def test_action_flows_through_execution(self) -> None:
        action = Action(
            description="Determine how to harvest hay.",
            action_type="plan",
        )

        objective = CurrentObjective(
            description="Harvest 100 units of hay.",
            source_objective_id="objective_hay",
        )

        builder = ActionRequestBuilder()

        request = builder.build(
            action=action,
            objective=objective,
            experiment_instructions=(
                "Use only capabilities available "
                "inside the experiment environment."
            ),
            observation=(
                "No detailed environment observation "
                "is currently available."
            ),
        )

        executor = DeterministicExecutor()

        result = executor.execute(request)

        self.assertTrue(result.success)

        self.assertEqual(
            result.request_id,
            request.request_id,
        )

        self.assertEqual(
            result.output["instruction"],
            action.description,
        )

        self.assertEqual(
            result.output["context"]["current_objective"],
            objective.description,
        )

        self.assertEqual(
            result.output["context"]["experiment_instructions"],
            (
                "Use only capabilities available "
                "inside the experiment environment."
            ),
        )

        self.assertEqual(
            result.output["context"]["observation"],
            (
                "No detailed environment observation "
                "is currently available."
            ),
        )


if __name__ == "__main__":
    unittest.main()