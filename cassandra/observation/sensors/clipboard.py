"""Sensor that captures text from the Windows clipboard."""

from __future__ import annotations

from typing import Any

import win32clipboard

from cassandra.observation.sensors.base import Sensor


class ClipboardSensor(Sensor):
    """Capture text currently available on the Windows clipboard."""

    @property
    def name(self) -> str:
        """Return the sensor's stable identifier."""

        return "clipboard"

    def capture(self) -> dict[str, Any]:
        """Capture clipboard text and basic metadata."""

        win32clipboard.OpenClipboard()

        try:
            if not win32clipboard.IsClipboardFormatAvailable(
                win32clipboard.CF_UNICODETEXT
            ):
                return {
                    "available": False,
                    "text": None,
                    "length": 0,
                }

            text = win32clipboard.GetClipboardData(
                win32clipboard.CF_UNICODETEXT
            )

            return {
                "available": True,
                "text": text,
                "length": len(text),
            }

        finally:
            win32clipboard.CloseClipboard()