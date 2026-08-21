"""Tests for Cassandra objective selection."""

from __future__ import annotations

import unittest

from cassandra.experiments import Mission, Objective
from cassandra.planner import ObjectiveSelector


class ObjectiveSelectorTests(unittest.TestCase):
    """Verify mission objective selection."""

    def setUp(self) -> None:
        self.selector = ObjectiveSelector()

    def test_highest_priority_objective_is_selected(self) -> None:
        mission = Mission(
            goal="Build a sustainable farm.",
            objectives=[
                Objective(
                    "Maintain sustainable yield.",
                    priority=2,
                ),
                Objective(
                    "Expand the farm.",
                    priority=1,
                ),
            ],
        )

        current = self.selector.select(mission)

        self.assertIsNotNone(current)
        self.assertEqual(
            current.description,
            "Expand the farm.",
        )
        self.assertEqual(
            current.status,
            "pending",
        )

    def test_selected_objective_preserves_source_id(self) -> None:
        objective = Objective(
            "Expand the farm.",
            priority=1,
        )

        mission = Mission(
            goal="Build a sustainable farm.",
            objectives=[objective],
        )

        current = self.selector.select(mission)

        self.assertIsNotNone(current)
        self.assertEqual(
            current.source_objective_id,
            objective.objective_id,
        )

    def test_empty_mission_returns_none(self) -> None:
        mission = Mission(
            goal="Observe the environment.",
            objectives=[],
        )

        current = self.selector.select(mission)

        self.assertIsNone(current)


if __name__ == "__main__":
    unittest.main()