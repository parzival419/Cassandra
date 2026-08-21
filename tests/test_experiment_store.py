"""Tests for Cassandra experiment persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cassandra.experiments import (
    Experiment,
    ExperimentStore,
    Mission,
    Objective,
)


class ExperimentStoreTests(unittest.TestCase):
    """Verify experiment persistence."""

    def _experiment(self) -> Experiment:
        mission = Mission(
            goal="Build and maintain a sustainable farm.",
            objectives=[
                Objective(
                    "Expand the farm.",
                    priority=1,
                ),
                Objective(
                    "Maintain even yield.",
                    priority=2,
                ),
            ],
        )

        experiment = Experiment(
            name="Sustainable Farm",
            environment="The Farmer Was Replaced",
            mission=mission,
            metadata={
                "model": "test-model",
            },
        )

        experiment.start()

        return experiment

    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = ExperimentStore(
                output_directory=directory
            )

            original = self._experiment()

            path = store.save(original)
            loaded = store.load(path)

            self.assertEqual(
                loaded.experiment_id,
                original.experiment_id,
            )
            self.assertEqual(
                loaded.status,
                "running",
            )
            self.assertEqual(
                loaded.mission.mission_id,
                original.mission.mission_id,
            )
            self.assertEqual(
                len(loaded.mission.objectives),
                2,
            )

    def test_metadata_survives_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = ExperimentStore(
                output_directory=directory
            )

            original = self._experiment()

            path = store.save(original)
            loaded = store.load(path)

            self.assertEqual(
                loaded.metadata["model"],
                "test-model",
            )

    def test_missing_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = ExperimentStore(
                output_directory=directory
            )

            missing = Path(directory) / "missing.json"

            with self.assertRaises(FileNotFoundError):
                store.load(missing)


if __name__ == "__main__":
    unittest.main()