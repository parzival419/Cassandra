"""Tests for Cassandra execution cycles."""

from __future__ import annotations

import unittest

from cassandra.execution import (
    ActionRequestBuilder,
    DeterministicExecutor,
    ExecutionCycle,
)
from cassandra.planner import (
    Action,
    ActionSelector,
    CurrentObjective,
    Plan,
)


class ExecutionCycleTests(unittest.TestCase):
    """Verify execution of one Cassandra plan action."""

    def setUp(self) -> None:
        self.objective = CurrentObjective(
            description="Harvest 100 units of hay.",
            source_objective_id="objective_hay",
        )

        self.plan = Plan(
            description="Progress toward harvesting hay.",
            objective_run_id=self.objective.objective_run_id,
        )

        self.action = Action(
            description="Determine how to harvest hay.",
            action_type="plan",
        )

        self.plan.add_action(self.action)

        self.cycle = ExecutionCycle(
            action_selector=ActionSelector(),
            request_builder=ActionRequestBuilder(),
            executor=DeterministicExecutor(),
        )

    def test_execute_returns_action_result(self) -> None:
        result = self.cycle.execute(
            plan=self.plan,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertTrue(result.success)

    def test_selected_action_is_activated(self) -> None:
        self.cycle.execute(
            plan=self.plan,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            self.action.status,
            "active",
        )

    def test_result_contains_selected_action_instruction(self) -> None:
        result = self.cycle.execute(
            plan=self.plan,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            result.output["instruction"],
            self.action.description,
        )

    def test_execution_does_not_complete_action(self) -> None:
        self.cycle.execute(
            plan=self.plan,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            self.action.status,
            "active",
        )

    def test_no_pending_action_returns_none(self) -> None:
        empty_plan = Plan(
            description="Empty plan.",
            objective_run_id=self.objective.objective_run_id,
        )

        result = self.cycle.execute(
            plan=empty_plan,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()