"""Sensor that captures the Windows virtual desktop as an image."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from PIL import ImageGrab

from cassandra.observation.sensors.base import Sensor


class ScreenshotSensor(Sensor):
    """Capture the complete virtual desktop and save it as a PNG."""

    def __init__(
        self,
        output_directory: str | Path = "artifacts/screenshots",
    ) -> None:
        self._output_directory = Path(output_directory)

    @property
    def name(self) -> str:
        """Return the sensor's stable identifier."""

        return "screenshot"

    def capture(self) -> dict[str, Any]:
        """Capture and persist the current virtual desktop."""

        captured_at = datetime.now(timezone.utc)

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"{captured_at:%Y%m%dT%H%M%S_%fZ}_"
            f"{uuid4().hex[:8]}.png"
        )

        screenshot_path = self._output_directory / filename

        image = ImageGrab.grab(all_screens=True)

        try:
            image.save(
                screenshot_path,
                format="PNG",
            )

            width, height = image.size

            return {
                "available": True,
                "path": str(screenshot_path.resolve()),
                "format": "PNG",
                "width": width,
                "height": height,
                "resolution": {
                    "width": width,
                    "height": height,
                },
                "captured_at": captured_at.isoformat(),
            }
        finally:
            image.close()