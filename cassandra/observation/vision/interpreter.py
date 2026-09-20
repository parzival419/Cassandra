"""Vision interpretation interfaces for Cassandra."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from cassandra.observation.vision.models import VisualObservation


class VisionInterpreter(Protocol):
    """Define the contract for Cassandra vision interpreters."""

    def interpret(
        self,
        image_path: Path,
    ) -> VisualObservation:
        """Interpret an image as structured visual evidence."""
        ...


class DeterministicVisionInterpreter:
    """Provide predictable visual interpretation for testing."""

    def interpret(
        self,
        image_path: Path,
    ) -> VisualObservation:
        """Return a deterministic visual observation."""

        return VisualObservation(
            metadata={
                "source_image": str(image_path),
                "interpreter": "deterministic",
            },
        )