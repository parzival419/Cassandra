"""Public interface for Cassandra evaluation rules."""

from cassandra.evaluation.rules.foreground_window import (
    ForegroundWindowRule,
)

__all__ = [
    "ForegroundWindowRule",
]