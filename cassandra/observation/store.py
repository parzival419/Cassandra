"""Persist Cassandra observations to disk."""

from __future__ import annotations

import json
from pathlib import Path

from cassandra.observation.models import Observation


class ObservationStore:
    """Save structured observations as JSON files."""

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