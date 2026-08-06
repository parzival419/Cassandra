"""Domain models for Cassandra behavioral episodes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from cassandra.memory.behavior.models import BehaviorEvent


@dataclass(slots=True)
class BehaviorEpisode:
    """Represent a meaningful period of related behavioral activity."""

    episode_type: str
    title: str
    started_at: datetime
    events: list[BehaviorEvent] = field(default_factory=list)
    ended_at: datetime | None = None
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    episode_id: str = field(
        default_factory=lambda: f"episode_{uuid4().hex}"
    )

    def __post_init__(self) -> None:
        """Validate and normalize the episode."""

        self.episode_type = self.episode_type.strip()
        self.title = self.title.strip()
        self.summary = self.summary.strip()

        if not self.episode_type:
            raise ValueError(
                "BehaviorEpisode requires a non-empty episode_type."
            )

        if not self.title:
            raise ValueError(
                "BehaviorEpisode requires a non-empty title."
            )

        if self.started_at.tzinfo is None:
            raise ValueError(
                "BehaviorEpisode started_at must be timezone-aware."
            )

        if self.ended_at is not None:
            if self.ended_at.tzinfo is None:
                raise ValueError(
                    "BehaviorEpisode ended_at must be timezone-aware."
                )

            if self.ended_at < self.started_at:
                raise ValueError(
                    "BehaviorEpisode ended_at cannot precede started_at."
                )

        self.events.sort(
            key=lambda event: event.timestamp
        )

    @property
    def is_active(self) -> bool:
        """Return whether the episode is still open."""

        return self.ended_at is None

    @property
    def event_count(self) -> int:
        """Return the number of events in the episode."""

        return len(self.events)

    @property
    def duration_seconds(self) -> float | None:
        """Return the completed episode duration in seconds."""

        if self.ended_at is None:
            return None

        duration = self.ended_at - self.started_at
        return round(duration.total_seconds(), 3)

    def add_event(self, event: BehaviorEvent) -> None:
        """Add a unique event to the episode."""

        if any(
            existing.event_id == event.event_id
            for existing in self.events
        ):
            raise ValueError(
                f"Duplicate event id in episode: {event.event_id}"
            )

        if event.timestamp < self.started_at:
            raise ValueError(
                "Behavior event cannot occur before the episode starts."
            )

        if (
            self.ended_at is not None
            and event.timestamp > self.ended_at
        ):
            raise ValueError(
                "Behavior event cannot occur after the episode ends."
            )

        self.events.append(event)
        self.events.sort(
            key=lambda existing: existing.timestamp
        )

    def close(
        self,
        ended_at: datetime | None = None,
    ) -> None:
        """Close the episode at a timezone-aware timestamp."""

        if not self.is_active:
            raise ValueError(
                "BehaviorEpisode is already closed."
            )

        resolved_end = ended_at or datetime.now(timezone.utc)

        if resolved_end.tzinfo is None:
            raise ValueError(
                "BehaviorEpisode ended_at must be timezone-aware."
            )

        if resolved_end < self.started_at:
            raise ValueError(
                "BehaviorEpisode ended_at cannot precede started_at."
            )

        self.ended_at = resolved_end

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        data = asdict(self)

        data["started_at"] = self.started_at.isoformat()
        data["ended_at"] = (
            self.ended_at.isoformat()
            if self.ended_at is not None
            else None
        )
        data["events"] = [
            event.to_dict()
            for event in self.events
        ]
        data["is_active"] = self.is_active
        data["event_count"] = self.event_count
        data["duration_seconds"] = self.duration_seconds

        return data