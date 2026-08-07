"""Classify behavioral episodes using deterministic evidence."""

from __future__ import annotations

from dataclasses import dataclass

from cassandra.memory.behavior.episodes import BehaviorEpisode


@dataclass(slots=True)
class EpisodeClassification:
    """Represent the classification assigned to a behavioral episode."""

    episode_type: str
    title: str
    confidence: str
    reason: str


class EpisodeClassifier:
    """Classify behavioral episodes from structured event evidence."""

    CODE_EXTENSIONS = {
        ".py",
        ".ps1",
        ".psm1",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".go",
        ".rs",
        ".java",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
    }

    GAMING_APPLICATIONS = {
        "The Farmer Was Replaced",
        "TheFarmerWasReplaced",
    }

    RESEARCH_APPLICATIONS = {
        "Google Chrome",
        "Microsoft Edge",
        "Firefox",
    }

    def classify(
        self,
        episode: BehaviorEpisode,
    ) -> EpisodeClassification:
        """Classify an episode using the strongest available evidence."""

        if self._looks_like_coding(episode):
            return EpisodeClassification(
                episode_type="coding_session",
                title="Coding Session",
                confidence="high",
                reason=(
                    "The episode contains document activity involving "
                    "recognized source-code or configuration file types."
                ),
            )

        if self._looks_like_gaming(episode):
            return EpisodeClassification(
                episode_type="gaming_session",
                title="Gaming Session",
                confidence="high",
                reason=(
                    "The episode contains application activity associated "
                    "with a recognized game environment."
                ),
            )

        if self._looks_like_research(episode):
            return EpisodeClassification(
                episode_type="research_session",
                title="Research Session",
                confidence="medium",
                reason=(
                    "The episode contains browser activity without stronger "
                    "evidence for another session type."
                ),
            )

        return EpisodeClassification(
            episode_type="general_session",
            title="General Session",
            confidence="low",
            reason=(
                "The available behavioral evidence does not strongly match "
                "a more specific session type."
            ),
        )

    def apply(
        self,
        episode: BehaviorEpisode,
    ) -> EpisodeClassification:
        """Classify an episode and apply the result to the episode."""

        classification = self.classify(episode)

        episode.episode_type = classification.episode_type
        episode.title = classification.title
        episode.metadata["classification"] = {
            "confidence": classification.confidence,
            "reason": classification.reason,
            "classifier": "deterministic_v1",
        }

        return classification

    def _looks_like_coding(
        self,
        episode: BehaviorEpisode,
    ) -> bool:
        """Return whether the episode contains strong coding evidence."""

        for event in episode.events:
            if event.event_type != "document_changed":
                continue

            for value in (event.before, event.after):
                if not isinstance(value, str):
                    continue

                lowered = value.lower()

                if any(
                    lowered.endswith(extension)
                    for extension in self.CODE_EXTENSIONS
                ):
                    return True

        return False

    def _looks_like_gaming(
        self,
        episode: BehaviorEpisode,
    ) -> bool:
        """Return whether the episode contains recognized gaming activity."""

        for event in episode.events:
            if event.event_type != "application_changed":
                continue

            values = {
                value
                for value in (event.before, event.after)
                if isinstance(value, str)
            }

            if values & self.GAMING_APPLICATIONS:
                return True

        return False

    def _looks_like_research(
        self,
        episode: BehaviorEpisode,
    ) -> bool:
        """Return whether the episode contains browser activity."""

        for event in episode.events:
            if event.event_type != "application_changed":
                continue

            values = {
                value
                for value in (event.before, event.after)
                if isinstance(value, str)
            }

            if values & self.RESEARCH_APPLICATIONS:
                return True

        return False