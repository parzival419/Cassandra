"""Build structured observations from sensor results."""

from __future__ import annotations

from typing import Any

from cassandra.observation.models import (
    EnvironmentInfo,
    Observation,
    VisualData,
)
from cassandra.observation.normalization import WindowNormalizer


class ObservationBuilder:
    """Assemble sensor results into an Observation domain object."""

    def __init__(
        self,
        environment: EnvironmentInfo,
        window_normalizer: WindowNormalizer | None = None,
    ) -> None:
        self._environment = environment
        self._window_normalizer = (
            window_normalizer or WindowNormalizer()
        )

        self._visual = VisualData()
        self._state: dict[str, Any] = {}
        self._evidence: dict[str, Any] = {}
        self._metadata: dict[str, Any] = {}
        self._successful_sensors: list[str] = []

    def add_sensor_result(
        self,
        sensor_name: str,
        result: dict[str, Any],
    ) -> None:
        """Place a successful sensor result into the correct domain field."""

        self._successful_sensors.append(sensor_name)

        match sensor_name:
            case "window":
                self._add_window_result(result)

            case "screenshot":
                self._add_screenshot_result(result)

            case _:
                self._evidence[sensor_name] = result

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        """Set metadata describing the observation process."""

        self._metadata = dict(metadata)

    @property
    def successful_sensor_count(self) -> int:
        """Return the number of successful sensor results."""

        return len(self._successful_sensors)

    def build(self) -> Observation:
        """Create the final structured observation."""

        return Observation(
            environment=self._environment,
            visual=self._visual,
            state=self._state,
            evidence=self._evidence,
            metadata=self._metadata,
            sensors=list(self._successful_sensors),
        )

    def _add_window_result(
        self,
        result: dict[str, Any],
    ) -> None:
        """Preserve raw window data and add normalized meaning."""

        raw_title = result.get("title")

        if not isinstance(raw_title, str):
            raw_title = None

        normalized = self._window_normalizer.normalize(
            raw_title
        )

        self._state["window"] = {
            "raw": dict(result),
            "normalized": normalized.to_dict(),
        }

    def _add_screenshot_result(
        self,
        result: dict[str, Any],
    ) -> None:
        """Map screenshot evidence into the VisualData domain object."""

        resolution = result.get("resolution")

        if isinstance(resolution, dict):
            width = resolution.get("width")
            height = resolution.get("height")

            if isinstance(width, int) and isinstance(height, int):
                self._visual.resolution = (width, height)

        screenshot_path = result.get("path")

        if isinstance(screenshot_path, str):
            self._visual.screenshot_path = screenshot_path

        self._evidence["screenshot"] = result