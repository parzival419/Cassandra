"""Tests for Cassandra experiment domain models."""

from __future__ import annotations

import unittest

from cassandra.experiments import Experiment, Mission, Objective


class ExperimentTests(unittest.TestCase):
    """Verify experiment domain behavior."""

    def _mission(self) -> Mission:
        return Mission(
            goal="Build and maintain a sustainable farm.",
            objectives=[
                Objective(
                    description="Expand the farm.",
                    priority=1,
                ),
                Objective(
                    description="Maintain sustainable yield.",
                    priority=2,
                ),
            ],
        )

    def _experiment(self) -> Experiment:
        return Experiment(
            name="Sustainable Farm",
            environment="The Farmer Was Replaced",
            mission=self._mission(),
        )

    def test_experiment_starts_created(self) -> None:
        experiment = self._experiment()

        self.assertEqual(
            experiment.status,
            "created",
        )

    def test_experiment_can_start(self) -> None:
        experiment = self._experiment()

        experiment.start()

        self.assertEqual(
            experiment.status,
            "running",
        )

    def test_running_experiment_can_pause(self) -> None:
        experiment = self._experiment()

        experiment.start()
        experiment.pause()

        self.assertEqual(
            experiment.status,
            "paused",
        )

    def test_created_experiment_cannot_pause(self) -> None:
        experiment = self._experiment()

        with self.assertRaises(ValueError):
            experiment.pause()

    def test_experiment_can_complete(self) -> None:
        experiment = self._experiment()

        experiment.start()
        experiment.complete()

        self.assertEqual(
            experiment.status,
            "completed",
        )

    def test_completed_experiment_cannot_restart(self) -> None:
        experiment = self._experiment()

        experiment.start()
        experiment.complete()

        with self.assertRaises(ValueError):
            experiment.start()

    def test_objectives_are_sorted_by_priority(self) -> None:
        mission = Mission(
            goal="Test mission.",
            objectives=[
                Objective("Second objective.", priority=2),
                Objective("First objective.", priority=1),
            ],
        )

        self.assertEqual(
            mission.objectives[0].description,
            "First objective.",
        )

    def test_experiment_serializes_mission(self) -> None:
        experiment = self._experiment()

        data = experiment.to_dict()

        self.assertEqual(
            data["mission"]["goal"],
            "Build and maintain a sustainable farm.",
        )

        self.assertEqual(
            len(data["mission"]["objectives"]),
            2,
        )


if __name__ == "__main__":
    unittest.main()