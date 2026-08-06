"""Persist and retrieve Cassandra behavioral timelines."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from cassandra.evaluation import ConfidenceLevel
from cassandra.memory.behavior.models import BehaviorEvent
from cassandra.memory.behavior.timeline import BehaviorTimeline


class TimelineStore:
    """Save and retrieve behavioral timelines as JSON files."""

    def __init__(
        self,
        output_directory: str | Path = "artifacts/timelines",
    ) -> None:
        self._output_directory = Path(output_directory)

    def save(
        self,
        timeline: BehaviorTimeline,
        name: str = "behavior_timeline",
    ) -> Path:
        """Serialize and save a behavioral timeline."""

        clean_name = name.strip()

        if not clean_name:
            raise ValueError(
                "Timeline name must not be empty."
            )

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            self._output_directory
            / f"{clean_name}.json"
        )

        with destination.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(
                timeline.to_dict(),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return destination.resolve()

    def load(
        self,
        path: str | Path,
    ) -> BehaviorTimeline:
        """Load a behavioral timeline from a JSON file."""

        source = Path(path)

        if not source.exists():
            raise FileNotFoundError(
                f"Timeline file does not exist: {source}"
            )

        if not source.is_file():
            raise ValueError(
                f"Timeline path is not a file: {source}"
            )

        with source.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Timeline file must contain a JSON object: {source}"
            )

        raw_events = data.get("events")

        if not isinstance(raw_events, list):
            raise ValueError(
                f"Timeline file must contain an events list: {source}"
            )

        timeline = BehaviorTimeline()

        for raw_event in raw_events:
            timeline.add(
                self._deserialize_event(raw_event)
            )

        return timeline

    def load_default(self) -> BehaviorTimeline:
        """Load the default behavioral timeline."""

        path = (
            self._output_directory
            / "behavior_timeline.json"
        )

        return self.load(path)

    def load_or_create(self) -> BehaviorTimeline:
        """Load the default timeline or return an empty one."""

        try:
            return self.load_default()
        except FileNotFoundError:
            return BehaviorTimeline()

    def _deserialize_event(
        self,
        data: Any,
    ) -> BehaviorEvent:
        """Convert serialized event data into a BehaviorEvent."""

        if not isinstance(data, dict):
            raise ValueError(
                "Each timeline event must be a JSON object."
            )

        try:
            confidence = ConfidenceLevel(
                data["confidence"]
            )

            timestamp = datetime.fromisoformat(
                data["timestamp"]
            )

            return BehaviorEvent(
                event_type=data["event_type"],
                title=data["title"],
                summary=data["summary"],
                confidence=confidence,
                rule_name=data["rule_name"],
                source_path=data["source_path"],
                previous_observation_id=(
                    data["previous_observation_id"]
                ),
                current_observation_id=(
                    data["current_observation_id"]
                ),
                before=data.get("before"),
                after=data.get("after"),
                metadata=data.get("metadata", {}),
                event_id=data["event_id"],
                timestamp=timestamp,
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Timeline contains an invalid behavior event."
            ) from exc