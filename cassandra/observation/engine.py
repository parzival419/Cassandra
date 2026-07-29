from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class ObservationEngine:
    """Coordinates environment observations."""

    def observe(self) -> dict[str, Any]:
        """
        Return a basic observation record.

        This is intentionally simple for now. Sensors will be added later.
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "observation captured",
            "sensors": {},
        }