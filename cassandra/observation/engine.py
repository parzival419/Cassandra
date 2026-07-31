"""Coordinates sensors and produces structured observations."""

from cassandra.observation.models import (
    EnvironmentInfo,
    Observation,
)


class ObservationEngine:
    """Creates observations from an environment and its sensors."""

    def __init__(self, environment: EnvironmentInfo) -> None:
        self._environment = environment

    def observe(self) -> Observation:
        """Capture and return the current observation."""

        return Observation(
            environment=self._environment,
            metadata={
                "status": "observation captured",
            },
        )