"""Build behavioral timeline events from evaluation results."""

from __future__ import annotations

from cassandra.evaluation import EvaluationResult, Finding
from cassandra.memory.behavior.models import BehaviorEvent
from cassandra.memory.behavior.timeline import BehaviorTimeline
from cassandra.memory.behavior.classifier import EpisodeClassifier


class TimelineBuilder:
    """Convert evaluation findings into behavioral timeline events."""

    EVENT_TYPE_BY_RULE = {
        "foreground_application_change": "application_changed",
        "active_document_change": "document_changed",
    }

    def build_events(
        self,
        result: EvaluationResult,
    ) -> list[BehaviorEvent]:
        """Convert all findings in an evaluation result into events."""

        return [
            self._build_event(
                finding=finding,
                result=result,
            )
            for finding in result.findings
        ]

    def add_to_timeline(
        self,
        result: EvaluationResult,
        timeline: BehaviorTimeline,
    ) -> list[BehaviorEvent]:
        """Build events and add them to an existing timeline."""

        events = self.build_events(result)

        for event in events:
            timeline.add(event)

        return events

    def _build_event(
        self,
        finding: Finding,
        result: EvaluationResult,
    ) -> BehaviorEvent:
        """Convert one evaluation finding into a behavior event."""

        event_type = self.EVENT_TYPE_BY_RULE.get(
            finding.rule_name,
            finding.rule_name,
        )

        return BehaviorEvent(
            event_type=event_type,
            title=finding.title,
            summary=finding.summary,
            confidence=finding.confidence,
            rule_name=finding.rule_name,
            source_path=finding.source_path,
            previous_observation_id=(
                result.previous_observation_id
            ),
            current_observation_id=(
                result.current_observation_id
            ),
            before=finding.before,
            after=finding.after,
            metadata={
                "evaluation_id": result.evaluation_id,
                "finding_id": finding.finding_id,
            },
            timestamp=result.timestamp,
        )