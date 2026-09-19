"""Execution result models for Cassandra."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class ActionResult:
    """Represent the result of an execution request."""

    request_id: str
    success: bool

    output: Any = None
    error: str | None = None

    result_id: str = field(
        default_factory=lambda: f"result_{uuid4().hex}"
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validate and normalize the execution result."""

        self.request_id = self.request_id.strip()

        if not self.request_id:
            raise ValueError(
                "ActionResult requires a request id."
            )

        if self.error is not None:
            self.error = self.error.strip()

            if not self.error:
                self.error = None

        if self.success and self.error is not None:
            raise ValueError(
                "Successful ActionResult cannot contain an error."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return asdict(self)