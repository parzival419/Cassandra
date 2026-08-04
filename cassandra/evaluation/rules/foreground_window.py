"""Rule for interpreting foreground-application changes."""

from __future__ import annotations

from cassandra.evaluation.finding import (
    ConfidenceLevel,
    Finding,
)
from cassandra.evaluation.rule import EvaluationRule
from cassandra.observation.comparison import ObservationDifference


class ForegroundWindowRule(EvaluationRule):
    """Interpret a change to the normalized foreground application."""

    TARGET_PATH = "state.window.normalized.application"

    @property
    def name(self) -> str:
        """Return the rule's stable identifier."""

        return "foreground_application_change"

    def evaluate(
        self,
        difference: ObservationDifference,
    ) -> list[Finding]:
        """Return findings for foreground-application changes."""

        findings: list[Finding] = []

        for change in difference.changes:
            if change.path != self.TARGET_PATH:
                continue

            if change.before is None or change.after is None:
                continue

            findings.append(
                Finding(
                    title="Foreground application changed",
                    summary=(
                        "The active foreground application changed."
                    ),
                    reason=(
                        "The normalized foreground application differed "
                        "between the previous and current observations."
                    ),
                    confidence=ConfidenceLevel.HIGH,
                    rule_name=self.name,
                    source_path=change.path,
                    before=change.before,
                    after=change.after,
                )
            )

        return findings