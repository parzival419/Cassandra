"""Structured summaries of Cassandra behavioral episodes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class BehaviorSummary:
    """Structured summary derived from a behavioral episode."""

    episode_id: str
    episode_type: str
    title: str

    event_count: int
    duration_seconds: float | None

    documents: list[str] = field(default_factory=list)

    document_change_count: int = 0
    document_modified_count: int = 0
    document_saved_count: int = 0
    application_change_count: int = 0

    interpretation: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the behavioral summary."""

        return asdict(self)