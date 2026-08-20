"""Build structured summaries from behavioral episodes."""

from __future__ import annotations

from cassandra.memory.behavior.episodes import BehaviorEpisode
from cassandra.memory.behavior.summary import BehaviorSummary


class BehaviorSummarizer:
    """Convert behavioral episodes into deterministic summaries."""

    ACTIVE_DOCUMENT_RULE = "active_document_change"
    FOREGROUND_APPLICATION_RULE = "foreground_application_change"
    DIRTY_STATE_RULE = "document_dirty_state"

    DOCUMENT_MODIFIED_TITLE = "Document modified"
    DOCUMENT_SAVED_TITLE = "Document saved"

    def summarize(
        self,
        episode: BehaviorEpisode,
    ) -> BehaviorSummary:
        """Build a structured summary for one episode."""

        documents: set[str] = set()

        document_change_count = 0
        document_modified_count = 0
        document_saved_count = 0
        application_change_count = 0

        for event in episode.events:
            if event.rule_name == self.ACTIVE_DOCUMENT_RULE:
                document_change_count += 1

                self._collect_document(
                    documents,
                    event.before,
                )
                self._collect_document(
                    documents,
                    event.after,
                )

            elif (
                event.rule_name
                == self.FOREGROUND_APPLICATION_RULE
            ):
                application_change_count += 1

            elif event.rule_name == self.DIRTY_STATE_RULE:
                if event.title == self.DOCUMENT_MODIFIED_TITLE:
                    document_modified_count += 1

                elif event.title == self.DOCUMENT_SAVED_TITLE:
                    document_saved_count += 1

        ordered_documents = sorted(
            documents,
            key=str.casefold,
        )

        interpretation = self._interpret(
            episode=episode,
            document_change_count=document_change_count,
            document_modified_count=document_modified_count,
            document_saved_count=document_saved_count,
            application_change_count=application_change_count,
        )

        return BehaviorSummary(
            episode_id=episode.episode_id,
            episode_type=episode.episode_type,
            title=episode.title,
            event_count=episode.event_count,
            duration_seconds=episode.duration_seconds,
            documents=ordered_documents,
            document_change_count=document_change_count,
            document_modified_count=document_modified_count,
            document_saved_count=document_saved_count,
            application_change_count=application_change_count,
            interpretation=interpretation,
            metadata={
                "summarizer": "deterministic_v1",
                "episode_active": episode.is_active,
            },
        )

    def _collect_document(
        self,
        documents: set[str],
        value: object,
    ) -> None:
        """Add a normalized document name when available."""

        if not isinstance(value, str):
            return

        document = value.strip()

        if document:
            documents.add(document)

    def _interpret(
        self,
        episode: BehaviorEpisode,
        document_change_count: int,
        document_modified_count: int,
        document_saved_count: int,
        application_change_count: int,
    ) -> str:
        """Generate a deterministic behavioral interpretation."""

        if (
            document_modified_count > 0
            or document_saved_count > 0
        ):
            return (
                "The episode contains active document editing "
                "and save-related behavior."
            )

        if document_change_count > 0:
            return (
                "The episode contains activity across one or more "
                "documents."
            )

        if application_change_count > 0:
            return (
                "The episode contains foreground application "
                "transitions."
            )

        if episode.event_count > 0:
            return (
                "The episode contains recorded behavioral activity."
            )

        return "The episode contains no recorded behavioral events."