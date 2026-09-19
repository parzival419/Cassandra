"""Tests for Cassandra experiment instructions."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cassandra.experiments import ExperimentInstructions


class ExperimentInstructionsTests(unittest.TestCase):
    """Verify experiment instruction loading."""

    def test_load_returns_instruction_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "experiment.md"

            path.write_text(
                "# Test Experiment\n\nTest instructions.",
                encoding="utf-8",
            )

            instructions = ExperimentInstructions(path)

            self.assertEqual(
                instructions.load(),
                "# Test Experiment\n\nTest instructions.",
            )

    def test_surrounding_whitespace_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "experiment.md"

            path.write_text(
                "\n\n# Test Experiment\n\n",
                encoding="utf-8",
            )

            instructions = ExperimentInstructions(path)

            self.assertEqual(
                instructions.load(),
                "# Test Experiment",
            )

    def test_missing_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.md"

            instructions = ExperimentInstructions(path)

            with self.assertRaises(FileNotFoundError):
                instructions.load()

    def test_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            instructions = ExperimentInstructions(
                temp_dir
            )

            with self.assertRaises(ValueError):
                instructions.load()

    def test_empty_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "experiment.md"

            path.write_text(
                "   \n   ",
                encoding="utf-8",
            )

            instructions = ExperimentInstructions(path)

            with self.assertRaises(ValueError):
                instructions.load()


if __name__ == "__main__":
    unittest.main()