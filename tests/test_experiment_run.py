"""Tests for Cassandra experiment runs."""

from __future__ import annotations

import unittest

from cassandra.experiments import ExperimentRun
from cassandra.planner import CurrentObjective, Plan


class ExperimentRunTests(unittest.TestCase):
    """Verify experiment run lifecycle and state."""

    def test_run_starts_created(self) -> None:
        run = ExperimentRun("experiment_test")

        self.assertEqual(run.status, "created")
        self.assertTrue(run.run_id.startswith("run_"))

    def test_created_run_can_start(self) -> None:
        run = ExperimentRun("experiment_test")

        run.start()

        self.assertEqual(run.status, "running")
        self.assertIsNotNone(run.started_at)

    def test_running_run_can_pause(self) -> None:
        run = ExperimentRun("experiment_test")
        run.start()

        run.pause()

        self.assertEqual(run.status, "paused")

    def test_paused_run_can_resume(self) -> None:
        run = ExperimentRun("experiment_test")
        run.start()
        run.pause()

        run.resume()

        self.assertEqual(run.status, "running")

    def test_running_run_can_complete(self) -> None:
        run = ExperimentRun("experiment_test")
        run.start()

        run.complete()

        self.assertEqual(run.status, "completed")

    def test_running_run_can_fail(self) -> None:
        run = ExperimentRun("experiment_test")
        run.start()

        run.fail()

        self.assertEqual(run.status, "failed")

    def test_blank_experiment_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ExperimentRun("   ")

    def test_invalid_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ExperimentRun(
                "experiment_test",
                status="invalid",
            )

    def test_current_objective_can_be_set(self) -> None:
        run = ExperimentRun("experiment_test")

        objective = CurrentObjective(
            "Expand the farm.",
            "objective_test",
        )

        run.set_current_objective(objective)

        self.assertIs(
            run.current_objective,
            objective,
        )

    def test_current_plan_can_be_set(self) -> None:
        run = ExperimentRun("experiment_test")

        objective = CurrentObjective(
            "Expand the farm.",
            "objective_test",
        )

        plan = Plan(
            "Inspect and expand.",
            objective.objective_run_id,
        )

        run.set_current_plan(plan)

        self.assertIs(
            run.current_plan,
            plan,
        )

    def test_serialization_includes_runtime_state(self) -> None:
        objective = CurrentObjective(
            "Expand the farm.",
            "objective_test",
        )

        plan = Plan(
            "Inspect and expand.",
            objective.objective_run_id,
        )

        run = ExperimentRun(
            "experiment_test",
            current_objective=objective,
            current_plan=plan,
            metadata={
                "environment": "farmer",
            },
        )

        run.start()

        serialized = run.to_dict()

        self.assertEqual(
            serialized["experiment_id"],
            "experiment_test",
        )
        self.assertEqual(
            serialized["status"],
            "running",
        )
        self.assertEqual(
            serialized["current_objective"]["description"],
            "Expand the farm.",
        )
        self.assertEqual(
            serialized["current_plan"]["description"],
            "Inspect and expand.",
        )
        self.assertEqual(
            serialized["metadata"],
            {"environment": "farmer"},
        )
        self.assertIsNotNone(
            serialized["started_at"]
        )


if __name__ == "__main__":
    unittest.main()