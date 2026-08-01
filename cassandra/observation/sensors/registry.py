"""Registry for configuring Cassandra observation sensors."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from cassandra.observation.sensors.base import Sensor


class SensorRegistry:
    """Maintain an ordered collection of uniquely named sensors."""

    def __init__(
        self,
        sensors: Iterable[Sensor] | None = None,
    ) -> None:
        self._sensors: dict[str, Sensor] = {}

        for sensor in sensors or ():
            self.register(sensor)

    def register(self, sensor: Sensor) -> None:
        """Register a sensor under its stable identifier."""

        if sensor.name in self._sensors:
            raise ValueError(
                f"Sensor is already registered: {sensor.name}"
            )

        self._sensors[sensor.name] = sensor

    def unregister(self, name: str) -> Sensor:
        """Remove and return a registered sensor."""

        try:
            return self._sensors.pop(name)
        except KeyError as exc:
            raise KeyError(
                f"Sensor is not registered: {name}"
            ) from exc

    def get(self, name: str) -> Sensor:
        """Return a registered sensor by name."""

        try:
            return self._sensors[name]
        except KeyError as exc:
            raise KeyError(
                f"Sensor is not registered: {name}"
            ) from exc

    def sensors(self) -> tuple[Sensor, ...]:
        """Return registered sensors in registration order."""

        return tuple(self._sensors.values())

    def names(self) -> tuple[str, ...]:
        """Return registered sensor identifiers."""

        return tuple(self._sensors)

    def __contains__(self, name: object) -> bool:
        return name in self._sensors

    def __iter__(self) -> Iterator[Sensor]:
        return iter(self._sensors.values())

    def __len__(self) -> int:
        return len(self._sensors)