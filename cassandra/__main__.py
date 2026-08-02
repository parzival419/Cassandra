"""Command-line entry point for Cassandra."""

from __future__ import annotations

from pprint import pprint

from cassandra.about import APP_NAME, VERSION, DESCRIPTION
from cassandra.observation import EnvironmentInfo, ObservationEngine
from cassandra.observation.sensors import (
    ClipboardSensor,
    ScreenshotSensor,
    SensorRegistry,
    TimeSensor,
    WindowSensor,
)


def build_sensor_registry() -> SensorRegistry:
    """Build the default sensor profile."""

    registry = SensorRegistry()

    registry.register(TimeSensor())
    registry.register(WindowSensor())
    registry.register(ScreenshotSensor())
    registry.register(ClipboardSensor())

    return registry

def main() -> None:
    """Start Cassandra."""

    print(f"{APP_NAME} v{VERSION}")
    print(DESCRIPTION)
    print()

    environment = EnvironmentInfo(
        name="Development Sandbox",
        type="simulated",
    )

    registry = build_sensor_registry()

    print(f"Environment : {environment.name}")
    print(f"Sensors     : {len(registry)}")
    print()

    for sensor in registry:
        print(f"✓ {sensor.name}")

    print()
    print("Collecting observation...\n")

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