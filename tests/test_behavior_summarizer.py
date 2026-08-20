"""Tests for deterministic behavioral episode summaries."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from cassandra.evaluation.finding import ConfidenceLevel
from cassandra.memory.behavior import (
    BehaviorEpisode,
    BehaviorEvent,
    BehaviorSummarizer,
)


class BehaviorSummarizerTests(unittest.TestCase):
    """Verify deterministic behavioral episode summarization."""

    def setUp(self) -> None:
        self.summarizer = BehaviorSummarizer()
        self.started_at = datetime(
            2026,
            8,
            19,
            12,
            0,
            tzinfo=timezone.utc,
        )

    def _event(
        self,
        *,
        rule_name: str,
        title: str,
        before: object = None,
        after: object = None,
        seconds: int = 0,
    ) -> BehaviorEvent:
        return BehaviorEvent(
            event_type="behavior",
            title=title,
            summary="Test behavioral event.",
            confidence=ConfidenceLevel.HIGH,
            rule_name=rule_name,
            source_path="state.window.normalized",
            previous_observation_id="obs_previous",
            current_observation_id="obs_current",
            before=before,
            after=after,
            timestamp=(
                self.started_at
                + timedelta(seconds=seconds)
            ),
        )

    def _episode(
        self,
        events: list[BehaviorEvent],
    ) -> BehaviorEpisode:
        return BehaviorEpisode(
            episode_type="coding_session",
            title="Coding Session",
            started_at=self.started_at,
            events=events,
        )

    def test_document_change_is_counted(self) -> None:
        episode = self._episode(
            [
                self._event(
                    rule_name="active_document_change",
                    title="Active document changed",
                    before="main.py",
                    after="README.md",
                ),
            ]
        )

        summary = self.summarizer.summarize(episode)

        self.assertEqual(
            summary.document_change_count,
            1,
        )
        self.assertEqual(
            summary.documents,
            ["main.py", "README.md"],
        )

    def test_documents_are_deduplicated(self) -> None:
        episode = self._episode(
            [
                self._event(
                    rule_name="active_document_change",
                    title="Active document changed",
                    before="main.py",
                    after="README.md",
                    seconds=1,
                ),
                self._event(
                    rule_name="active_document_change",
                    title="Active document changed",
                    before="README.md",
                    after="main.py",
                    seconds=2,
                ),
            ]
        )

        summary = self.summarizer.summarize(episode)

        self.assertEqual(
            summary.documents,
            ["main.py", "README.md"],
        )
        self.assertEqual(
            summary.document_change_count,
            2,
        )

    def test_modified_and_saved_events_are_counted(
        self,
    ) -> None:
        episode = self._episode(
            [
                self._event(
                    rule_name="document_dirty_state",
                    title="Document modified",
                    before=False,
                    after=True,
                    seconds=1,
                ),
                self._event(
                    rule_name="document_dirty_state",
                    title="Document saved",
                    before=True,
                    after=False,
                    seconds=2,
                ),
            ]
        )

        summary = self.summarizer.summarize(episode)

        self.assertEqual(
            summary.document_modified_count,
            1,
        )
        self.assertEqual(
            summary.document_saved_count,
            1,
        )
        self.assertEqual(
            summary.interpretation,
            (
                "The episode contains active document editing "
                "and save-related behavior."
            ),
        )

    def test_application_change_is_counted(self) -> None:
        episode = self._episode(
            [
                self._event(
                    rule_name="foreground_application_change",
                    title="Foreground application changed",
                    before="Visual Studio Code",
                    after="Microsoft Edge",
                ),
            ]
        )

        summary = self.summarizer.summarize(episode)

        self.assertEqual(
            summary.application_change_count,
            1,
        )
        self.assertEqual(
            summary.interpretation,
            (
                "The episode contains foreground application "
                "transitions."
            ),
        )

    def test_empty_episode_produces_empty_summary(
        self,
    ) -> None:
        episode = self._episode([])

        summary = self.summarizer.summarize(episode)

        self.assertEqual(summary.event_count, 0)
        self.assertEqual(summary.documents, [])
        self.assertEqual(
            summary.document_change_count,
            0,
        )
        self.assertEqual(
            summary.document_modified_count,
            0,
        )
        self.assertEqual(
            summary.document_saved_count,
            0,
        )
        self.assertEqual(
            summary.application_change_count,
            0,
        )
        self.assertEqual(
            summary.interpretation,
            (
                "The episode contains no recorded "
                "behavioral events."
            ),
        )


if __name__ == "__main__":
    unittest.main()