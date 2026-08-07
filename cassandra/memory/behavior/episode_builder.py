"""Build behavioral episodes from timeline events."""

from __future__ import annotations

from datetime import timedelta

from cassandra.memory.behavior.classifier import EpisodeClassifier
from cassandra.memory.behavior.episodes import BehaviorEpisode
from cassandra.memory.behavior.models import BehaviorEvent
from cassandra.memory.behavior.timeline import BehaviorTimeline


class EpisodeBuilder:
    """Group chronologically related behavior events into episodes."""

    def __init__(
        self,
        inactivity_threshold: timedelta = timedelta(minutes=10),
    ) -> None:
        if inactivity_threshold.total_seconds() <= 0:
            raise ValueError(
                "Episode inactivity threshold must be greater than zero."
            )

        self._inactivity_threshold = inactivity_threshold
        self._classifier = EpisodeClassifier()

    def build(
        self,
        timeline: BehaviorTimeline,
    ) -> list[BehaviorEpisode]:
        """Build episodes from all events in a behavior timeline."""

        return self.build_from_events(
            list(timeline)
        )

    def build_from_events(
        self,
        events: list[BehaviorEvent],
    ) -> list[BehaviorEpisode]:
        """Build episodes from a collection of behavioral events."""

        if not events:
            return []

        ordered_events = sorted(
            events,
            key=lambda event: event.timestamp,
        )

        episodes: list[BehaviorEpisode] = []

        current_episode = self._start_episode(
            ordered_events[0]
        )

        for event in ordered_events[1:]:
            previous_event = current_episode.events[-1]
            gap = event.timestamp - previous_event.timestamp

            if gap <= self._inactivity_threshold:
                current_episode.add_event(event)
                continue

            current_episode.close(
                ended_at=previous_event.timestamp
            )

            self._classifier.apply(current_episode)
            episodes.append(current_episode)

            current_episode = self._start_episode(event)

        self._classifier.apply(current_episode)
        episodes.append(current_episode)

        return episodes

    def _start_episode(
        self,
        event: BehaviorEvent,
    ) -> BehaviorEpisode:
        """Create a new active episode beginning with an event."""

        episode = BehaviorEpisode(
            episode_type="behavior_session",
            title="Behavior Session",
            started_at=event.timestamp,
            metadata={
                "builder": "inactivity_threshold",
                "inactivity_threshold_seconds": (
                    self._inactivity_threshold.total_seconds()
                ),
            },
        )

        episode.add_event(event)

        return episode