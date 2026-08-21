"""Planner objective models for Cassandra."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class CurrentObjective:
    """Represent the planner's active objective."""

    description: str
    source_objective_id: str

    status: str = "pending"

    objective_run_id: str = field(
        default_factory=lambda: f"objective_run_{uuid4().hex}"
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    VALID_STATUSES = {
        "pending",
        "active",
        "completed",
        "failed",
    }

    def __post_init__(self) -> None:
        """Validate and normalize the current objective."""

        self.description = self.description.strip()
        self.source_objective_id = (
            self.source_objective_id.strip()
        )
        self.status = self.status.strip().lower()

        if not self.description:
            raise ValueError(
                "CurrentObjective requires a non-empty description."
            )

        if not self.source_objective_id:
            raise ValueError(
                "CurrentObjective requires a source objective id."
            )

        if self.status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid objective status: {self.status}"
            )

    def activate(self) -> None:
        """Mark the objective as active."""

        if self.status != "pending":
            raise ValueError(
                "Only pending objectives can be activated."
            )

        self.status = "active"

    def complete(self) -> None:
        """Mark the objective as completed."""

        if self.status != "active":
            raise ValueError(
                "Only active objectives can be completed."
            )

        self.status = "completed"

    def fail(self) -> None:
        """Mark the objective as failed."""

        if self.status != "active":
            raise ValueError(
                "Only active objectives can fail."
            )

        self.status = "failed"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return asdict(self)