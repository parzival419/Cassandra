"""Sensor that captures the current UTC time."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from cassandra.observation.sensors.base import Sensor


class TimeSensor(Sensor):
    """Capture the current timezone-aware UTC timestamp."""

    @property
    def name(self) -> str:
        """Return the sensor's stable identifier."""

        return "time"

    def capture(self) -> dict[str, Any]:
        """Capture the current UTC time."""

        captured_at = datetime.now(timezone.utc)

        return {
            "timestamp": captured_at.isoformat(),
            "timezone": "UTC",
        }