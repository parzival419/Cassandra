"""Planner plan models for Cassandra."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from cassandra.planner.action import Action


@dataclass(slots=True)
class Plan:
    """Represent a plan for accomplishing a current objective."""

    description: str
    objective_run_id: str

    actions: list[Action] = field(
        default_factory=list
    )

    status: str = "pending"

    plan_id: str = field(
        default_factory=lambda: f"plan_{uuid4().hex}"
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
        """Validate and normalize the plan."""

        self.description = self.description.strip()
        self.objective_run_id = self.objective_run_id.strip()
        self.status = self.status.strip().lower()

        if not self.description:
            raise ValueError(
                "Plan requires a non-empty description."
            )

        if not self.objective_run_id:
            raise ValueError(
                "Plan requires an objective run id."
            )

        if self.status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid plan status: {self.status}"
            )

    def add_action(self, action: Action) -> None:
        """Append an action to the plan."""

        self.actions.append(action)

    def activate(self) -> None:
        """Mark the plan as active."""

        if self.status != "pending":
            raise ValueError(
                "Only pending plans can be activated."
            )

        self.status = "active"

    def complete(self) -> None:
        """Mark the plan as completed."""

        if self.status != "active":
            raise ValueError(
                "Only active plans can be completed."
            )

        self.status = "completed"

    def fail(self) -> None:
        """Mark the plan as failed."""

        if self.status != "active":
            raise ValueError(
                "Only active plans can fail."
            )

        self.status = "failed"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return {
            "description": self.description,
            "objective_run_id": self.objective_run_id,
            "actions": [
                action.to_dict()
                for action in self.actions
            ],
            "status": self.status,
            "plan_id": self.plan_id,
            "metadata": self.metadata,
        }