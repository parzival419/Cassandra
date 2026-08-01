"""Command-line entry point for Cassandra."""

from __future__ import annotations

from pprint import pprint

from cassandra.observation import EnvironmentInfo, ObservationEngine
from cassandra.observation.sensors import TimeSensor


def main() -> None:
    """Start Cassandra and capture a test observation."""

    print("Starting Cassandra...\n")

    environment = EnvironmentInfo(
        name="Development Sandbox",
        type="simulated",
    )

    engine = ObservationEngine(
        environment=environment,
        sensors=[
            TimeSensor(),
        ],
    )

    observation = engine.observe()

    pprint(
        observation.to_dict(),
        sort_dicts=False,
    )


if __name__ == "__main__":
    main()