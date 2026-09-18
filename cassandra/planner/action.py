"""Planner action models for Cassandra."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class Action:
    """Represent an action proposed by a Cassandra plan."""

    description: str
    action_type: str

    status: str = "pending"

    action_id: str = field(
        default_factory=lambda: f"action_{uuid4().hex}"
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
        """Validate and normalize the action."""

        self.description = self.description.strip()
        self.action_type = self.action_type.strip().lower()
        self.status = self.status.strip().lower()

        if not self.description:
            raise ValueError(
                "Action requires a non-empty description."
            )

        if not self.action_type:
            raise ValueError(
                "Action requires a non-empty action type."
            )

        if self.status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid action status: {self.status}"
            )

    def activate(self) -> None:
        """Mark the action as active."""

        if self.status != "pending":
            raise ValueError(
                "Only pending actions can be activated."
            )

        self.status = "active"

    def complete(self) -> None:
        """Mark the action as completed."""

        if self.status != "active":
            raise ValueError(
                "Only active actions can be completed."
            )

        self.status = "completed"

    def fail(self) -> None:
        """Mark the action as failed."""

        if self.status != "active":
            raise ValueError(
                "Only active actions can fail."
            )

        self.status = "failed"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return asdict(self)