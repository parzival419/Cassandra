"""Public interface for Cassandra evaluation rules."""

from cassandra.evaluation.rules.active_document import ActiveDocumentRule
from cassandra.evaluation.rules.foreground_window import (
    ForegroundWindowRule,
)

__all__ = [
    "ActiveDocumentRule",
    "ForegroundWindowRule",
]