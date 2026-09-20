"""Environment integration for The Farmer Was Replaced."""

from __future__ import annotations

import win32gui


class FarmerEnvironment:
    """Represent The Farmer Was Replaced environment."""

    WINDOW_TITLE = "TheFarmerWasReplaced"

    def locate(self) -> int:
        """Return the Farmer window handle when available."""

        return win32gui.FindWindow(
            None,
            self.WINDOW_TITLE,
        )

    def is_available(self) -> bool:
        """Return whether the Farmer window is available and visible."""

        window_handle = self.locate()

        if not window_handle:
            return False

        return bool(
            win32gui.IsWindowVisible(window_handle)
        )

    def bounds(
        self,
    ) -> tuple[int, int, int, int] | None:
        """Return the Farmer window bounds when available."""

        window_handle = self.locate()

        if not window_handle:
            return None

        return win32gui.GetWindowRect(
            window_handle
        )