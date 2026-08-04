"""Domain models for Cassandra evaluation findings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any
from uuid import uuid4


class ConfidenceLevel(str, Enum):
    """Supported confidence levels for evaluation findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class Finding:
    """Represent an interpreted meaning derived from observed changes."""

    title: str
    summary: str
    reason: str
    confidence: ConfidenceLevel
    rule_name: str
    source_path: str
    before: Any = None
    after: Any = None
    finding_id: str = ""

    def __post_init__(self) -> None:
        """Assign a unique identifier when one was not supplied."""

        if not self.finding_id:
            self.finding_id = f"finding_{uuid4().hex}"

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        data = asdict(self)
        data["confidence"] = self.confidence.value
        return data