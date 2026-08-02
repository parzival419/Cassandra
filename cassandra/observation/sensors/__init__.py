"""Public interface for Cassandra observation sensors."""

from cassandra.observation.sensors.base import Sensor
from cassandra.observation.sensors.clipboard import ClipboardSensor
from cassandra.observation.sensors.registry import SensorRegistry
from cassandra.observation.sensors.screenshot import ScreenshotSensor
from cassandra.observation.sensors.time import TimeSensor
from cassandra.observation.sensors.window import WindowSensor

__all__ = [
    "ClipboardSensor",
    "ScreenshotSensor",
    "Sensor",
    "SensorRegistry",
    "TimeSensor",
    "WindowSensor",
]