"""Base contract for Cassandra evaluation rules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cassandra.evaluation.finding import Finding
from cassandra.observation.comparison import ObservationDifference


class EvaluationRule(ABC):
    """Abstract base class for interpreting observation differences."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the rule's stable identifier."""

    @abstractmethod
    def evaluate(
        self,
        difference: ObservationDifference,
    ) -> list[Finding]:
        """Evaluate an observation difference and return findings."""