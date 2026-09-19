"""Tests for Cassandra action request construction."""

from __future__ import annotations

import unittest

from cassandra.execution import ActionRequestBuilder
from cassandra.planner import Action, CurrentObjective


class ActionRequestBuilderTests(unittest.TestCase):
    """Verify translation of planning state into execution requests."""

    def setUp(self) -> None:
        self.action = Action(
            description="Determine how to harvest hay.",
            action_type="plan",
        )

        self.objective = CurrentObjective(
            description="Harvest 100 units of hay.",
            source_objective_id="objective_hay",
        )

        self.builder = ActionRequestBuilder()

    def test_build_returns_action_request(self) -> None:
        request = self.builder.build(
            action=self.action,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            request.action_id,
            self.action.action_id,
        )

    def test_action_description_becomes_instruction(self) -> None:
        request = self.builder.build(
            action=self.action,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            request.instruction,
            "Determine how to harvest hay.",
        )

    def test_context_contains_objective(self) -> None:
        request = self.builder.build(
            action=self.action,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            request.context["current_objective"],
            "Harvest 100 units of hay.",
        )

    def test_context_contains_experiment_instructions(self) -> None:
        request = self.builder.build(
            action=self.action,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            request.context["experiment_instructions"],
            "Experiment rules.",
        )

    def test_context_contains_observation(self) -> None:
        request = self.builder.build(
            action=self.action,
            objective=self.objective,
            experiment_instructions="Experiment rules.",
            observation="Current environment state.",
        )

        self.assertEqual(
            request.context["observation"],
            "Current environment state.",
        )


if __name__ == "__main__":
    unittest.main()