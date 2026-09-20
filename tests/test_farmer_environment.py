"""Tests for The Farmer Was Replaced environment."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from cassandra.environments import FarmerEnvironment


class FarmerEnvironmentTests(unittest.TestCase):
    """Verify Farmer environment discovery."""

    @patch("cassandra.environments.farmer.win32gui")
    def test_is_available_when_window_exists(
        self,
        win32gui,
    ) -> None:
        win32gui.FindWindow.return_value = 12345
        win32gui.IsWindowVisible.return_value = True

        environment = FarmerEnvironment()

        self.assertTrue(environment.is_available())

    @patch("cassandra.environments.farmer.win32gui")
    def test_is_unavailable_when_window_missing(
        self,
        win32gui,
    ) -> None:
        win32gui.FindWindow.return_value = 0

        environment = FarmerEnvironment()

        self.assertFalse(environment.is_available())

    @patch("cassandra.environments.farmer.win32gui")
    def test_locate_returns_window_handle(
        self,
        win32gui,
    ) -> None:
        win32gui.FindWindow.return_value = 12345

        environment = FarmerEnvironment()

        self.assertEqual(
            environment.locate(),
            12345,
        )

        win32gui.FindWindow.assert_called_once_with(
            None,
            "TheFarmerWasReplaced",
        )

    @patch("cassandra.environments.farmer.win32gui")
    def test_bounds_returns_window_coordinates(
        self,
        win32gui,
    ) -> None:
        win32gui.FindWindow.return_value = 12345
        win32gui.GetWindowRect.return_value = (
            537,
            -1058,
            2233,
            8,
        )

        environment = FarmerEnvironment()

        self.assertEqual(
            environment.bounds(),
            (537, -1058, 2233, 8),
        )

    @patch("cassandra.environments.farmer.win32gui")
    def test_bounds_returns_none_when_window_missing(
        self,
        win32gui,
    ) -> None:
        win32gui.FindWindow.return_value = 0

        environment = FarmerEnvironment()

        self.assertIsNone(environment.bounds())


if __name__ == "__main__":
    unittest.main()