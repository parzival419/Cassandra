"""Structured visual observation models for Cassandra."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VisualCounter:
    """Represent a counter observed in a visual environment."""

    value: int | float
    identity: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the counter."""

        return {
            "value": self.value,
            "identity": self.identity,
        }


@dataclass(slots=True)
class VisualObservation:
    """Represent structured evidence extracted from an image."""

    screen_state: str | None = None
    visible_text: list[str] = field(default_factory=list)
    counters: list[VisualCounter] = field(default_factory=list)
    visible_elements: list[str] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the visual observation."""

        return {
            "screen_state": self.screen_state,
            "visible_text": list(self.visible_text),
            "counters": [
                counter.to_dict()
                for counter in self.counters
            ],
            "visible_elements": list(self.visible_elements),
            "uncertainties": list(self.uncertainties),
            "metadata": dict(self.metadata),
        }