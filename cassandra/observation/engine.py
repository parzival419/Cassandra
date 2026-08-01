"""Coordinate sensors and produce structured observations."""

from __future__ import annotations

from collections.abc import Iterable
from time import perf_counter
from typing import Any

from cassandra.observation.models import EnvironmentInfo, Observation
from cassandra.observation.sensors import Sensor


class ObservationEngine:
    """Run observation sensors and assemble their evidence."""

    def __init__(
        self,
        environment: EnvironmentInfo,
        sensors: Iterable[Sensor] | None = None,
    ) -> None:
        self._environment = environment
        self._sensors = tuple(sensors or ())

        self._validate_sensor_names()

    def observe(self) -> Observation:
        """Run all configured sensors and return one observation."""

        started_at = perf_counter()

        evidence, successful_sensors, sensor_errors = (
            self._collect_evidence()
        )

        duration_ms = round(
            (perf_counter() - started_at) * 1000,
            3,
        )

        metadata = self._build_metadata(
            duration_ms=duration_ms,
            successful_sensors=successful_sensors,
            sensor_errors=sensor_errors,
        )

        return self._create_observation(
            evidence=evidence,
            successful_sensors=successful_sensors,
            metadata=metadata,
        )

    def _collect_evidence(
        self,
    ) -> tuple[
        dict[str, Any],
        list[str],
        dict[str, dict[str, str]],
    ]:
        """Execute sensors and collect their evidence and errors."""

        evidence: dict[str, Any] = {}
        successful_sensors: list[str] = []
        sensor_errors: dict[str, dict[str, str]] = {}

        for sensor in self._sensors:
            try:
                evidence[sensor.name] = sensor.capture()
                successful_sensors.append(sensor.name)
            except Exception as exc:
                sensor_errors[sensor.name] = {
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }

        return evidence, successful_sensors, sensor_errors

    def _build_metadata(
        self,
        duration_ms: float,
        successful_sensors: list[str],
        sensor_errors: dict[str, dict[str, str]],
    ) -> dict[str, Any]:
        """Build metadata describing the observation process."""

        status = (
            "observation captured"
            if not sensor_errors
            else "observation captured with sensor errors"
        )

        metadata: dict[str, Any] = {
            "status": status,
            "duration_ms": duration_ms,
            "configured_sensor_count": len(self._sensors),
            "successful_sensor_count": len(successful_sensors),
            "failed_sensor_count": len(sensor_errors),
        }

        if sensor_errors:
            metadata["sensor_errors"] = sensor_errors

        return metadata

    def _create_observation(
        self,
        evidence: dict[str, Any],
        successful_sensors: list[str],
        metadata: dict[str, Any],
    ) -> Observation:
        """Create the final structured observation."""

        return Observation(
            environment=self._environment,
            evidence=evidence,
            metadata=metadata,
            sensors=successful_sensors,
        )

    def _validate_sensor_names(self) -> None:
        """Reject duplicate sensor identifiers."""

        sensor_names = [sensor.name for sensor in self._sensors]

        duplicate_names = {
            name
            for name in sensor_names
            if sensor_names.count(name) > 1
        }

        if duplicate_names:
            duplicates = ", ".join(sorted(duplicate_names))

            raise ValueError(
                f"Duplicate sensor names are not allowed: {duplicates}"
            )