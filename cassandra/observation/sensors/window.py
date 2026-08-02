"""Sensor that captures information about the active foreground window."""

from __future__ import annotations

from typing import Any

import win32gui

from cassandra.observation.sensors.base import Sensor


class WindowSensor(Sensor):
    """Capture basic metadata about the active Windows window."""

    @property
    def name(self) -> str:
        """Return the sensor's stable identifier."""

        return "window"

    def capture(self) -> dict[str, Any]:
        """Capture the active window handle, title, position, and size."""

        window_handle = win32gui.GetForegroundWindow()

        if not window_handle:
            return {
                "available": False,
                "handle": None,
                "title": None,
                "bounds": None,
                "width": None,
                "height": None,
            }

        title = win32gui.GetWindowText(window_handle).strip()
        left, top, right, bottom = win32gui.GetWindowRect(window_handle)

        width = max(0, right - left)
        height = max(0, bottom - top)

        return {
            "available": True,
            "handle": window_handle,
            "title": title or None,
            "bounds": {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
            },
            "width": width,
            "height": height,
        }