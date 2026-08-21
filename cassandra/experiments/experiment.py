"""Experiment domain model for Cassandra."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from cassandra.experiments.models import Mission


@dataclass(slots=True)
class Experiment:
    """Represent one controlled Cassandra experiment."""

    name: str
    environment: str
    mission: Mission

    status: str = "created"

    experiment_id: str = field(
        default_factory=lambda: f"experiment_{uuid4().hex}"
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    VALID_STATUSES = {
        "created",
        "running",
        "paused",
        "completed",
    }

    def __post_init__(self) -> None:
        """Validate and normalize the experiment."""

        self.name = self.name.strip()
        self.environment = self.environment.strip()
        self.status = self.status.strip().lower()

        if not self.name:
            raise ValueError(
                "Experiment requires a non-empty name."
            )

        if not self.environment:
            raise ValueError(
                "Experiment requires a non-empty environment."
            )

        if self.status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid experiment status: {self.status}"
            )

    def start(self) -> None:
        """Mark the experiment as running."""

        if self.status == "completed":
            raise ValueError(
                "Completed experiments cannot be restarted."
            )

        self.status = "running"

    def pause(self) -> None:
        """Pause a running experiment."""

        if self.status != "running":
            raise ValueError(
                "Only running experiments can be paused."
            )

        self.status = "paused"

    def complete(self) -> None:
        """Mark the experiment as completed."""

        self.status = "completed"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "environment": self.environment,
            "status": self.status,
            "mission": self.mission.to_dict(),
            "metadata": dict(self.metadata),
        }