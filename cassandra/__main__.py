"""Command-line entry point for Cassandra."""

from __future__ import annotations

from pprint import pprint

from cassandra.about import APP_NAME, DESCRIPTION, VERSION
from cassandra.evaluation import (
    EvaluationEngine,
    EvaluationResult,
    RuleRegistry,
)
from cassandra.evaluation.rules import (
    ActiveDocumentRule,
    ForegroundWindowRule,
)
from cassandra.memory.behavior import (
    TimelineBuilder,
    TimelineStore,
)
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
    registry.register(ActiveDocumentRule())

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


def update_behavior_timeline(
    evaluation_result: EvaluationResult,
) -> None:
    """Add evaluation findings to persistent behavioral memory."""

    timeline_store = TimelineStore()
    timeline = timeline_store.load_or_create()

    timeline_builder = TimelineBuilder()

    added_events = timeline_builder.add_to_timeline(
        result=evaluation_result,
        timeline=timeline,
    )

    timeline_path = timeline_store.save(timeline)

    print()
    print(f"Behavior timeline saved: {timeline_path}")
    print(f"Behavior events added   : {len(added_events)}")
    print(f"Behavior events remembered: {len(timeline)}")


def main() -> None:
    """Capture, persist, compare, evaluate, and remember behavior."""

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

    observation_store = ObservationStore()
    observation_path = observation_store.save(observation)

    pprint(
        observation.to_dict(),
        sort_dicts=False,
    )

    print()
    print(f"Observation saved: {observation_path}")

    try:
        previous, current = observation_store.latest_two()
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
    update_behavior_timeline(evaluation_result)


if __name__ == "__main__":
    main()