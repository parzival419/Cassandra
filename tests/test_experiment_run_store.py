"""Tests for Cassandra experiment run persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cassandra.experiments import (
    ExperimentRun,
    ExperimentRunStore,
)
from cassandra.planner import Action, CurrentObjective, Plan


class ExperimentRunStoreTests(unittest.TestCase):
    """Verify experiment run persistence and restoration."""

    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExperimentRunStore(temp_dir)

            objective = CurrentObjective(
                "Expand the farm.",
                "objective_expand",
            )
            objective.activate()

            plan = Plan(
                "Inspect the farm and expand east.",
                objective.objective_run_id,
            )

            plan.add_action(
                Action(
                    "Inspect the current farm.",
                    "observe",
                )
            )

            run = ExperimentRun(
                "experiment_farmer",
                current_objective=objective,
                current_plan=plan,
            )

            run.start()
            run.pause()

            store.save(run)

            loaded = store.load(
                run.experiment_id,
                run.run_id,
            )

            self.assertEqual(
                loaded.run_id,
                run.run_id,
            )
            self.assertEqual(
                loaded.experiment_id,
                run.experiment_id,
            )
            self.assertEqual(
                loaded.status,
                "paused",
            )
            self.assertEqual(
                loaded.current_objective.description,
                "Expand the farm.",
            )
            self.assertEqual(
                loaded.current_objective.status,
                "active",
            )
            self.assertEqual(
                loaded.current_plan.description,
                "Inspect the farm and expand east.",
            )
            self.assertEqual(
                loaded.current_plan.actions[0].description,
                "Inspect the current farm.",
            )

    def test_loaded_paused_run_can_resume(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExperimentRunStore(temp_dir)

            run = ExperimentRun(
                "experiment_test",
            )

            run.start()
            run.pause()

            store.save(run)

            loaded = store.load(
                run.experiment_id,
                run.run_id,
            )

            loaded.resume()

            self.assertEqual(
                loaded.status,
                "running",
            )

    def test_metadata_survives_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExperimentRunStore(temp_dir)

            run = ExperimentRun(
                "experiment_test",
                metadata={
                    "environment": "farmer",
                    "trial": 1,
                },
            )

            store.save(run)

            loaded = store.load(
                run.experiment_id,
                run.run_id,
            )

            self.assertEqual(
                loaded.metadata,
                {
                    "environment": "farmer",
                    "trial": 1,
                },
            )

    def test_timestamps_survive_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExperimentRunStore(temp_dir)

            run = ExperimentRun(
                "experiment_test",
            )

            run.start()
            store.save(run)

            loaded = store.load(
                run.experiment_id,
                run.run_id,
            )

            self.assertEqual(
                loaded.started_at,
                run.started_at,
            )
            self.assertEqual(
                loaded.updated_at,
                run.updated_at,
            )

    def test_missing_run_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExperimentRunStore(temp_dir)

            with self.assertRaises(FileNotFoundError):
                store.load(
                    "experiment_test",
                    "run_missing",
                )

    def test_save_creates_expected_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ExperimentRunStore(temp_dir)

            run = ExperimentRun(
                "experiment_test",
            )

            path = store.save(run)

            expected = (
                Path(temp_dir)
                / "experiment_test"
                / "runs"
                / f"{run.run_id}.json"
            )

            self.assertEqual(path, expected)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()