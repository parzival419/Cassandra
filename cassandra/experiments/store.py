"""Persist and retrieve Cassandra experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cassandra.experiments.experiment import Experiment
from cassandra.experiments.models import Mission, Objective


class ExperimentStore:
    """Save and retrieve experiment definitions as JSON."""

    def __init__(
        self,
        output_directory: str | Path = "artifacts/experiments",
    ) -> None:
        self._output_directory = Path(output_directory)

    def save(
        self,
        experiment: Experiment,
    ) -> Path:
        """Persist one experiment."""

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            self._output_directory
            / f"{experiment.experiment_id}.json"
        )

        with destination.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(
                experiment.to_dict(),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return destination.resolve()

    def load(
        self,
        path: str | Path,
    ) -> Experiment:
        """Load one experiment from JSON."""

        source = Path(path)

        if not source.exists():
            raise FileNotFoundError(
                f"Experiment file does not exist: {source}"
            )

        with source.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "Experiment file must contain a JSON object."
            )

        return self._deserialize(data)

    def _deserialize(
        self,
        data: dict[str, Any],
    ) -> Experiment:
        """Convert serialized data into an Experiment."""

        mission_data = data["mission"]

        objectives = [
            Objective(
                description=objective["description"],
                priority=objective["priority"],
                objective_id=objective["objective_id"],
            )
            for objective in mission_data.get(
                "objectives",
                [],
            )
        ]

        mission = Mission(
            goal=mission_data["goal"],
            objectives=objectives,
            constraints=mission_data.get(
                "constraints",
                [],
            ),
            mission_id=mission_data["mission_id"],
        )

        return Experiment(
            name=data["name"],
            environment=data["environment"],
            mission=mission,
            status=data["status"],
            experiment_id=data["experiment_id"],
            metadata=data.get("metadata", {}),
        )