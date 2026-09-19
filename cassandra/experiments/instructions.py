"""Experiment instruction loading for Cassandra."""

from __future__ import annotations

from pathlib import Path


class ExperimentInstructions:
    """Load human-readable instructions for an experiment."""

    def __init__(
        self,
        path: str | Path,
    ) -> None:
        self.path = Path(path)

    def load(self) -> str:
        """Load and return the experiment instructions."""

        if not self.path.exists():
            raise FileNotFoundError(self.path)

        if not self.path.is_file():
            raise ValueError(
                f"Experiment instruction path is not a file: {self.path}"
            )

        content = self.path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            raise ValueError(
                "Experiment instructions cannot be empty."
            )

        return content