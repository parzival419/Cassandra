"""Domain models used by Cassandra's observation subsystem."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class EnvironmentInfo:
    """Identifies the environment being observed."""

    name: str
    type: str
    version: str | None = None


@dataclass(slots=True)
class VisualData:
    """Visual information captured from the environment."""

    screenshot_path: str | None = None
    resolution: tuple[int, int] | None = None


@dataclass(slots=True)
class Observation:
    """A structured record of Cassandra's view of an environment."""

    environment: EnvironmentInfo
    visual: VisualData = field(default_factory=VisualData)
    state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    sensors: list[str] = field(default_factory=list)
    observation_id: str = field(
        default_factory=lambda: f"obs_{uuid4().hex}"
    )
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data