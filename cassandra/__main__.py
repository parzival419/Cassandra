"""Command-line entry point for Cassandra."""

from __future__ import annotations

from pprint import pprint

from cassandra.about import APP_NAME, DESCRIPTION, VERSION
from cassandra.evaluation import (
    EvaluationEngine,
    EvaluationResult,
    RuleRegistry,
)
from cassandra.evaluation.rules import ForegroundWindowRule
from cassandra.observation import (
    EnvironmentInfo,
    ObservationEngine,
    ObservationStore,
)
from cassandra.observation.comparer import ObservationComparer
from cassandra.observation.sensors import (
    ClipboardSensor,
    ScreenshotSensor,
    SensorRegistry,
    TimeSensor,
    WindowSensor,
)


def build_sensor_registry() -> SensorRegistry:
    """Build the default observation sensor profile."""

    registry = SensorRegistry()

    registry.register(TimeSensor())
    registry.register(WindowSensor())
    registry.register(ScreenshotSensor())
    registry.register(ClipboardSensor())

    return registry


def build_rule_registry() -> RuleRegistry:
    """Build the default evaluation rule profile."""

    registry = RuleRegistry()

    registry.register(ForegroundWindowRule())

    return registry


def print_evaluation_result(result: EvaluationResult) -> None:
    """Print findings produced by the evaluation engine."""

    print()
    print("Evaluation Findings")
    print("===================")
    print()

    if not result.has_findings:
        print("No meaningful findings detected.")
        return

    for index, finding in enumerate(result.findings, start=1):
        print(f"{index}. {finding.title}")
        print(f"   {finding.summary}")
        print(f"   Before     : {finding.before}")
        print(f"   After      : {finding.after}")
        print(f"   Confidence : {finding.confidence.value}")
        print(f"   Rule       : {finding.rule_name}")
        print()


def main() -> None:
    """Capture, persist, compare, and evaluate an observation."""

    print(f"{APP_NAME} v{VERSION}")
    print(DESCRIPTION)
    print()

    environment = EnvironmentInfo(
        name="Development Sandbox",
        type="simulated",
    )

    sensor_registry = build_sensor_registry()

    print(f"Environment : {environment.name}")
    print(f"Sensors     : {len(sensor_registry)}")
    print()

    for sensor in sensor_registry:
        print(f"✓ {sensor.name}")

    print()
    print("Collecting observation...\n")

    observation_engine = ObservationEngine(
        environment=environment,
        sensors=sensor_registry,
    )

    observation = observation_engine.observe()

    store = ObservationStore()
    observation_path = store.save(observation)

    pprint(
        observation.to_dict(),
        sort_dicts=False,
    )

    print()
    print(f"Observation saved: {observation_path}")

    try:
        previous, current = store.latest_two()
    except FileNotFoundError:
        print()
        print(
            "Evaluation skipped: at least two saved observations "
            "are required."
        )
        return

    difference = ObservationComparer().compare(
        previous=previous,
        current=current,
    )

    rule_registry = build_rule_registry()

    evaluation_engine = EvaluationEngine(
        rules=rule_registry,
    )

    evaluation_result = evaluation_engine.evaluate(
        difference,
    )

    print_evaluation_result(evaluation_result)


if __name__ == "__main__":
    main()