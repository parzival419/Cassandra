"""Compare persisted Cassandra observations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class FieldChange:
    """Represent a single changed field."""

    path: str
    before: Any
    after: Any

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return asdict(self)


@dataclass(slots=True)
class ObservationDifference:
    """Represent the differences between two observations."""

    previous_observation_id: str
    current_observation_id: str
    changes: list[FieldChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Return whether any differences were detected."""

        return bool(self.changes)

    @property
    def change_count(self) -> int:
        """Return the total number of changed fields."""

        return len(self.changes)

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        return {
            "previous_observation_id": self.previous_observation_id,
            "current_observation_id": self.current_observation_id,
            "has_changes": self.has_changes,
            "change_count": self.change_count,
            "changes": [
                change.to_dict()
                for change in self.changes
            ],
        }