"""Public interface for Cassandra observation sensors."""

from cassandra.observation.sensors.base import Sensor
from cassandra.observation.sensors.time import TimeSensor

__all__ = [
    "Sensor",
    "TimeSensor",
]