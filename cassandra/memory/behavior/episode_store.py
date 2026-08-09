"""Persist and retrieve Cassandra behavioral episodes."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from cassandra.evaluation import ConfidenceLevel
from cassandra.memory.behavior.episodes import BehaviorEpisode
from cassandra.memory.behavior.models import BehaviorEvent


class EpisodeStore:
    """Save and retrieve behavioral episodes as JSON."""

    def __init__(
        self,
        output_directory: str | Path = "artifacts/episodes",
    ) -> None:
        self._output_directory = Path(output_directory)

    def save(
        self,
        episodes: list[BehaviorEpisode],
        name: str = "behavior_episodes",
    ) -> Path:
        """Serialize and save behavioral episodes."""

        clean_name = name.strip()

        if not clean_name:
            raise ValueError(
                "Episode collection name must not be empty."
            )

        self._output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            self._output_directory
            / f"{clean_name}.json"
        )

        data = {
            "episode_count": len(episodes),
            "episodes": [
                episode.to_dict()
                for episode in episodes
            ],
        }

        with destination.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return destination.resolve()

    def load(
        self,
        path: str | Path,
    ) -> list[BehaviorEpisode]:
        """Load behavioral episodes from JSON."""

        source = Path(path)

        if not source.exists():
            raise FileNotFoundError(
                f"Episode file does not exist: {source}"
            )

        if not source.is_file():
            raise ValueError(
                f"Episode path is not a file: {source}"
            )

        with source.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "Episode file must contain a JSON object."
            )

        raw_episodes = data.get("episodes")

        if not isinstance(raw_episodes, list):
            raise ValueError(
                "Episode file must contain an episodes list."
            )

        return [
            self._deserialize_episode(raw_episode)
            for raw_episode in raw_episodes
        ]

    def load_default(self) -> list[BehaviorEpisode]:
        """Load the default episode collection."""

        path = (
            self._output_directory
            / "behavior_episodes.json"
        )

        return self.load(path)

    def load_or_create(self) -> list[BehaviorEpisode]:
        """Load saved episodes or return an empty collection."""

        try:
            return self.load_default()
        except FileNotFoundError:
            return []

    def _deserialize_episode(
        self,
        data: Any,
    ) -> BehaviorEpisode:
        """Convert serialized episode data into a BehaviorEpisode."""

        if not isinstance(data, dict):
            raise ValueError(
                "Each episode must be a JSON object."
            )

        raw_events = data.get("events", [])

        if not isinstance(raw_events, list):
            raise ValueError(
                "Episode events must be a list."
            )

        episode = BehaviorEpisode(
            episode_type=data["episode_type"],
            title=data["title"],
            started_at=datetime.fromisoformat(
                data["started_at"]
            ),
            ended_at=(
                datetime.fromisoformat(
                    data["ended_at"]
                )
                if data.get("ended_at")
                else None
            ),
            summary=data.get("summary", ""),
            metadata=data.get("metadata", {}),
            episode_id=data["episode_id"],
        )

        for raw_event in raw_events:
            episode.add_event(
                self._deserialize_event(raw_event)
            )

        return episode

    def _deserialize_event(
        self,
        data: Any,
    ) -> BehaviorEvent:
        """Convert serialized event data into a BehaviorEvent."""

        if not isinstance(data, dict):
            raise ValueError(
                "Each episode event must be a JSON object."
            )

        return BehaviorEvent(
            event_type=data["event_type"],
            title=data["title"],
            summary=data["summary"],
            confidence=ConfidenceLevel(
                data["confidence"]
            ),
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
            timestamp=datetime.fromisoformat(
                data["timestamp"]
            ),
        )