"""Persist and retrieve Cassandra observations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cassandra.observation.models import Observation


class ObservationStore:
    """Save and retrieve structured observations as JSON files."""

    def __init__(
        self,
        output_directory: str | Path = "artifacts/observations",
    ) -> None:
        self._output_directory = Path(output_directory)

    def save(self, observation: Observation) -> Path:
        """Serialize and save an observation as JSON."""

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            self._output_directory
            / f"{observation.observation_id}.json"
        )

        with destination.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(
                observation.to_dict(),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return destination.resolve()

    def load(self, path: str | Path) -> dict[str, Any]:
        """Load a saved observation from a JSON file."""

        source = Path(path)

        if not source.exists():
            raise FileNotFoundError(
                f"Observation file does not exist: {source}"
            )

        if not source.is_file():
            raise ValueError(
                f"Observation path is not a file: {source}"
            )

        with source.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Observation file must contain a JSON object: {source}"
            )

        return data

    def latest(self) -> Path:
        """Return the most recently modified observation file."""

        if not self._output_directory.exists():
            raise FileNotFoundError(
                "Observation directory does not exist: "
                f"{self._output_directory}"
            )

        observation_files = list(
            self._output_directory.glob("obs_*.json")
        )

        if not observation_files:
            raise FileNotFoundError(
                "No saved observations were found in: "
                f"{self._output_directory}"
            )

        return max(
            observation_files,
            key=lambda path: path.stat().st_mtime,
        ).resolve()

    def load_latest(self) -> dict[str, Any]:
        """Load the most recently saved observation."""

        return self.load(self.latest())