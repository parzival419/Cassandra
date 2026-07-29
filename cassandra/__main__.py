from __future__ import annotations

from pprint import pprint

from cassandra.observation.engine import ObservationEngine


def main() -> None:
    """Start Cassandra and capture a basic observation."""

    print("Starting Cassandra...")

    engine = ObservationEngine()
    observation = engine.observe()

    pprint(observation)


if __name__ == "__main__":
    main()