"""Experiment run models for Cassandra."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from cassandra.planner import CurrentObjective, Plan


@dataclass(slots=True)
class ExperimentRun:
    """Represent one execution run of a Cassandra experiment."""

    experiment_id: str

    current_objective: CurrentObjective | None = None
    current_plan: Plan | None = None

    status: str = "created"

    run_id: str = field(
        default_factory=lambda: f"run_{uuid4().hex}"
    )

    started_at: datetime | None = None

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    VALID_STATUSES = {
        "created",
        "running",
        "paused",
        "completed",
        "failed",
    }

    def __post_init__(self) -> None:
        """Validate and normalize the experiment run."""

        self.experiment_id = self.experiment_id.strip()
        self.status = self.status.strip().lower()

        if not self.experiment_id:
            raise ValueError(
                "ExperimentRun requires an experiment id."
            )

        if self.status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid experiment run status: {self.status}"
            )

    def start(self) -> None:
        """Start a newly created experiment run."""

        if self.status != "created":
            raise ValueError(
                "Only created experiment runs can be started."
            )

        now = datetime.now(timezone.utc)

        self.status = "running"
        self.started_at = now
        self.updated_at = now

    def pause(self) -> None:
        """Pause a running experiment run."""

        if self.status != "running":
            raise ValueError(
                "Only running experiment runs can be paused."
            )

        self.status = "paused"
        self._touch()

    def resume(self) -> None:
        """Resume a paused experiment run."""

        if self.status != "paused":
            raise ValueError(
                "Only paused experiment runs can be resumed."
            )

        self.status = "running"
        self._touch()

    def complete(self) -> None:
        """Complete a running experiment run."""

        if self.status != "running":
            raise ValueError(
                "Only running experiment runs can be completed."
            )

        self.status = "completed"
        self._touch()

    def fail(self) -> None:
        """Fail a running experiment run."""

        if self.status != "running":
            raise ValueError(
                "Only running experiment runs can fail."
            )

        self.status = "failed"
        self._touch()

    def set_current_objective(
        self,
        objective: CurrentObjective | None,
    ) -> None:
        """Set the run's current objective."""

        self.current_objective = objective
        self._touch()

    def set_current_plan(
        self,
        plan: Plan | None,
    ) -> None:
        """Set the run's current plan."""

        self.current_plan = plan
        self._touch()

    def _touch(self) -> None:
        """Update the run modification timestamp."""

        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return {
            "experiment_id": self.experiment_id,
            "current_objective": (
                self.current_objective.to_dict()
                if self.current_objective
                else None
            ),
            "current_plan": (
                self.current_plan.to_dict()
                if self.current_plan
                else None
            ),
            "status": self.status,
            "run_id": self.run_id,
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }