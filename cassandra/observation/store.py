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

        observation_files = self._sorted_observation_files()

        if not observation_files:
            raise FileNotFoundError(
                "No saved observations were found in: "
                f"{self._output_directory}"
            )

        return observation_files[-1].resolve()

    def latest_two(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Load the two newest observations in chronological order."""

        observation_files = self._sorted_observation_files()

        if len(observation_files) < 2:
            raise FileNotFoundError(
                "At least two saved observations are required in: "
                f"{self._output_directory}"
            )

        previous_path = observation_files[-2]
        current_path = observation_files[-1]

        previous = self.load(previous_path)
        current = self.load(current_path)

        return previous, current

    def load_latest(self) -> dict[str, Any]:
        """Load the most recently saved observation."""

        return self.load(self.latest())

    def _sorted_observation_files(self) -> list[Path]:
        """Return saved observation files ordered from oldest to newest."""

        if not self._output_directory.exists():
            raise FileNotFoundError(
                "Observation directory does not exist: "
                f"{self._output_directory}"
            )

        observation_files = list(
            self._output_directory.glob("obs_*.json")
        )

        return sorted(
            observation_files,
            key=lambda path: path.stat().st_mtime,
        )