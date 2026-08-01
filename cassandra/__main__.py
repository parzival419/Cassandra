"""Command-line entry point for Cassandra."""

from __future__ import annotations

from pprint import pprint

from cassandra.observation import EnvironmentInfo, ObservationEngine
from cassandra.observation.sensors import (
    ClipboardSensor,
    SensorRegistry,
    TimeSensor,
)


def build_sensor_registry() -> SensorRegistry:
    """Build the sensor profile used by the local demonstration."""

    registry = SensorRegistry()

    registry.register(TimeSensor())
    registry.register(ClipboardSensor())

    return registry


def main() -> None:
    """Start Cassandra and capture a test observation."""

    print("Starting Cassandra...\n")

    environment = EnvironmentInfo(
        name="Development Sandbox",
        type="simulated",
    )

    registry = build_sensor_registry()

    engine = ObservationEngine(
        environment=environment,
        sensors=registry,
    )

    observation = engine.observe()

    pprint(
        observation.to_dict(),
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()