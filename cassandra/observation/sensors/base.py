"""Base contract for Cassandra observation sensors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Sensor(ABC):
    """Abstract base class for components that collect evidence."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the sensor's stable identifier."""

    @abstractmethod
    def capture(self) -> dict[str, Any]:
        """Capture and return evidence from the environment."""