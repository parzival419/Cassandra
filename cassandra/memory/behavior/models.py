"""Domain models for Cassandra behavioral memory."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from cassandra.evaluation.finding import ConfidenceLevel


@dataclass(slots=True)
class BehaviorEvent:
    """Represent one meaningful event in a behavioral timeline."""

    event_type: str
    title: str
    summary: str
    confidence: ConfidenceLevel
    rule_name: str
    source_path: str
    previous_observation_id: str
    current_observation_id: str
    before: Any = None
    after: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(
        default_factory=lambda: f"event_{uuid4().hex}"
    )
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Validate required identifiers and normalize text fields."""

        self.event_type = self.event_type.strip()
        self.title = self.title.strip()
        self.summary = self.summary.strip()
        self.rule_name = self.rule_name.strip()
        self.source_path = self.source_path.strip()
        self.previous_observation_id = (
            self.previous_observation_id.strip()
        )
        self.current_observation_id = (
            self.current_observation_id.strip()
        )

        required_values = {
            "event_type": self.event_type,
            "title": self.title,
            "rule_name": self.rule_name,
            "source_path": self.source_path,
            "previous_observation_id": self.previous_observation_id,
            "current_observation_id": self.current_observation_id,
        }

        missing_fields = [
            name
            for name, value in required_values.items()
            if not value
        ]

        if missing_fields:
            fields = ", ".join(missing_fields)
            raise ValueError(
                f"BehaviorEvent requires non-empty fields: {fields}"
            )

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "BehaviorEvent timestamp must be timezone-aware."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        data = asdict(self)
        data["confidence"] = self.confidence.value
        data["timestamp"] = self.timestamp.isoformat()

        return data