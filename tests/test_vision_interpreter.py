"""Tests for Cassandra vision interpretation."""

from __future__ import annotations

from pathlib import Path

from cassandra.observation.vision import (
    DeterministicVisionInterpreter,
    VisualObservation,
)


def test_interpreter_returns_visual_observation() -> None:
    interpreter = DeterministicVisionInterpreter()

    result = interpreter.interpret(
        Path("farmer.png")
    )

    assert isinstance(
        result,
        VisualObservation,
    )


def test_interpreter_records_source_image() -> None:
    interpreter = DeterministicVisionInterpreter()

    result = interpreter.interpret(
        Path("farmer.png")
    )

    assert result.metadata["source_image"] == "farmer.png"


def test_interpreter_identifies_itself() -> None:
    interpreter = DeterministicVisionInterpreter()

    result = interpreter.interpret(
        Path("farmer.png")
    )

    assert (
        result.metadata["interpreter"]
        == "deterministic"
    )