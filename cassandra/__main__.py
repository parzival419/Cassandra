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
    EpisodeBuilder,
    EpisodeStore,
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


def print_evaluation_result(
    result: EvaluationResult,
) -> None:
    """Print findings produced by the evaluation engine."""

    print()
    print("Evaluation Findings")
    print("===================")
    print()

    if not result.has_findings:
        print("No meaningful findings detected.")
        return

    for index, finding in enumerate(
        result.findings,
        start=1,
    ):
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
    print(
        f"Behavior events remembered: "
        f"{len(timeline)}"
    )


def print_behavior_episodes() -> None:
    """Build, persist, and print classified behavioral episodes."""

    timeline_store = TimelineStore()
    timeline = timeline_store.load_or_create()

    episode_builder = EpisodeBuilder()
    episodes = episode_builder.build(timeline)

    episode_store = EpisodeStore()
    episode_path = episode_store.save(episodes)

    print()
    print("Behavior Episodes")
    print("=================")
    print()

    if not episodes:
        print("No behavioral episodes detected.")
        print()
        print(
            f"Behavior episodes saved: "
            f"{episode_path}"
        )
        return

    for index, episode in enumerate(
        episodes,
        start=1,
    ):
        classification = episode.metadata.get(
            "classification",
            {},
        )

        confidence = classification.get(
            "confidence",
            "unknown",
        )

        print(f"{index}. {episode.title}")
        print(
            f"   Type       : "
            f"{episode.episode_type}"
        )
        print(
            f"   Events     : "
            f"{episode.event_count}"
        )
        print(
            f"   Started    : "
            f"{episode.started_at.isoformat()}"
        )

        if episode.ended_at is None:
            print("   Ended      : active")
        else:
            print(
                f"   Ended      : "
                f"{episode.ended_at.isoformat()}"
            )

        if episode.duration_seconds is None:
            print("   Duration   : active")
        else:
            print(
                f"   Duration   : "
                f"{episode.duration_seconds} seconds"
            )

        print(
            f"   Confidence : "
            f"{confidence}"
        )
        print()

    print(
        f"Behavior episodes saved: "
        f"{episode_path}"
    )


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
    observation_path = observation_store.save(
        observation
    )

    pprint(
        observation.to_dict(),
        sort_dicts=False,
    )

    print()
    print(
        f"Observation saved: "
        f"{observation_path}"
    )

    try:
        previous, current = observation_store.latest_two()
    except FileNotFoundError:
        print()
        print(
            "Evaluation skipped: at least two saved "
            "observations are required."
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

    print_evaluation_result(
        evaluation_result
    )

    update_behavior_timeline(
        evaluation_result
    )

    print_behavior_episodes()


if __name__ == "__main__":
    main()