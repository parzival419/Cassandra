"""Execution request models for Cassandra."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class ActionRequest:
    """Represent a request to execute a planned action."""

    action_id: str
    instruction: str

    context: dict[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: f"request_{uuid4().hex}"
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validate and normalize the execution request."""

        self.action_id = self.action_id.strip()
        self.instruction = self.instruction.strip()

        if not self.action_id:
            raise ValueError(
                "ActionRequest requires an action id."
            )

        if not self.instruction:
            raise ValueError(
                "ActionRequest requires a non-empty instruction."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return asdict(self)