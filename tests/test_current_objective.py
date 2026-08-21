"""Tests for Cassandra planner current objectives."""

from __future__ import annotations

import unittest

from cassandra.planner import CurrentObjective


class CurrentObjectiveTests(unittest.TestCase):
    """Verify current-objective lifecycle behavior."""

    def _objective(self) -> CurrentObjective:
        return CurrentObjective(
            description="Expand the farm.",
            source_objective_id="objective_test",
        )

    def test_objective_starts_pending(self) -> None:
        objective = self._objective()

        self.assertEqual(
            objective.status,
            "pending",
        )

    def test_pending_objective_can_activate(self) -> None:
        objective = self._objective()

        objective.activate()

        self.assertEqual(
            objective.status,
            "active",
        )

    def test_active_objective_can_complete(self) -> None:
        objective = self._objective()

        objective.activate()
        objective.complete()

        self.assertEqual(
            objective.status,
            "completed",
        )

    def test_active_objective_can_fail(self) -> None:
        objective = self._objective()

        objective.activate()
        objective.fail()

        self.assertEqual(
            objective.status,
            "failed",
        )

    def test_pending_objective_cannot_complete(self) -> None:
        objective = self._objective()

        with self.assertRaises(ValueError):
            objective.complete()

    def test_pending_objective_cannot_fail(self) -> None:
        objective = self._objective()

        with self.assertRaises(ValueError):
            objective.fail()

    def test_completed_objective_cannot_reactivate(self) -> None:
        objective = self._objective()

        objective.activate()
        objective.complete()

        with self.assertRaises(ValueError):
            objective.activate()

    def test_blank_description_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CurrentObjective(
                description="   ",
                source_objective_id="objective_test",
            )

    def test_blank_source_objective_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CurrentObjective(
                description="Expand the farm.",
                source_objective_id="   ",
            )

    def test_invalid_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CurrentObjective(
                description="Expand the farm.",
                source_objective_id="objective_test",
                status="unknown",
            )

    def test_serialization_preserves_state(self) -> None:
        objective = self._objective()

        objective.activate()

        data = objective.to_dict()

        self.assertEqual(
            data["description"],
            "Expand the farm.",
        )
        self.assertEqual(
            data["source_objective_id"],
            "objective_test",
        )
        self.assertEqual(
            data["status"],
            "active",
        )
        self.assertTrue(
            data["objective_run_id"].startswith(
                "objective_run_"
            )
        )


if __name__ == "__main__":
    unittest.main()