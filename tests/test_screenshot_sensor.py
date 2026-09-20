"""Tests for Cassandra screenshot observation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from cassandra.observation.sensors.screenshot import ScreenshotSensor


class ScreenshotSensorTests(unittest.TestCase):
    """Verify screenshot capture behavior."""

    @patch(
        "cassandra.observation.sensors.screenshot.ImageGrab.grab"
    )
    def test_capture_region_uses_requested_bounds(
        self,
        grab,
    ) -> None:
        image = MagicMock()
        image.size = (1696, 1066)
        grab.return_value = image

        with tempfile.TemporaryDirectory() as directory:
            sensor = ScreenshotSensor(
                output_directory=directory,
            )

            result = sensor.capture_region(
                (
                    537,
                    -1058,
                    2233,
                    8,
                )
            )

        grab.assert_called_once_with(
            bbox=(
                537,
                -1058,
                2233,
                8,
            ),
            all_screens=True,
        )

        self.assertTrue(result["available"])
        self.assertEqual(
            result["width"],
            1696,
        )
        self.assertEqual(
            result["height"],
            1066,
        )

        image.save.assert_called_once()
        image.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()