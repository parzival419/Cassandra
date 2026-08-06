"""Behavior timeline domain model."""

from __future__ import annotations

from dataclasses import dataclass, field

from cassandra.memory.behavior.models import BehaviorEvent


@dataclass(slots=True)
class BehaviorTimeline:
    """Ordered collection of behavioral events."""

    events: list[BehaviorEvent] = field(default_factory=list)

    def add(self, event: BehaviorEvent) -> None:
        """Add an event to the timeline."""

        if any(
            existing.event_id == event.event_id
            for existing in self.events
        ):
            raise ValueError(
                f"Duplicate event id: {event.event_id}"
            )

        self.events.append(event)

        self.events.sort(
            key=lambda e: e.timestamp
        )

    def latest(self) -> BehaviorEvent | None:
        """Return the newest event."""

        if not self.events:
            return None

        return self.events[-1]

    def filter(
        self,
        event_type: str,
    ) -> list[BehaviorEvent]:
        """Return events of a given type."""

        return [
            event
            for event in self.events
            if event.event_type == event_type
        ]

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self):
        return iter(self.events)

    def to_dict(self) -> dict:
        """Serialize the timeline."""

        return {
            "event_count": len(self.events),
            "events": [
                event.to_dict()
                for event in self.events
            ],
        }