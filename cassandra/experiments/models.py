"""Domain models for Cassandra experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class Objective:
    """Represent one measurable objective within a mission."""

    description: str
    priority: int = 1
    objective_id: str = field(
        default_factory=lambda: f"objective_{uuid4().hex}"
    )

    def __post_init__(self) -> None:
        """Validate and normalize the objective."""

        self.description = self.description.strip()

        if not self.description:
            raise ValueError(
                "Objective requires a non-empty description."
            )

        if self.priority < 1:
            raise ValueError(
                "Objective priority must be greater than zero."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return asdict(self)


@dataclass(slots=True)
class Mission:
    """Represent the persistent goal assigned to an experiment."""

    goal: str
    objectives: list[Objective] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    mission_id: str = field(
        default_factory=lambda: f"mission_{uuid4().hex}"
    )

    def __post_init__(self) -> None:
        """Validate and normalize the mission."""

        self.goal = self.goal.strip()

        if not self.goal:
            raise ValueError(
                "Mission requires a non-empty goal."
            )

        self.constraints = [
            constraint.strip()
            for constraint in self.constraints
            if constraint.strip()
        ]

        self.objectives.sort(
            key=lambda objective: objective.priority
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return {
            "mission_id": self.mission_id,
            "goal": self.goal,
            "objectives": [
                objective.to_dict()
                for objective in self.objectives
            ],
            "constraints": list(self.constraints),
        }