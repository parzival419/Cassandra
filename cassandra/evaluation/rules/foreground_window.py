"""Rule for interpreting foreground-window title changes."""

from __future__ import annotations

from cassandra.evaluation.finding import (
    ConfidenceLevel,
    Finding,
)
from cassandra.evaluation.rule import EvaluationRule
from cassandra.observation.comparison import ObservationDifference


class ForegroundWindowRule(EvaluationRule):
    """Interpret a change to the foreground window title."""

    TARGET_PATH = "state.window.title"

    @property
    def name(self) -> str:
        """Return the rule's stable identifier."""

        return "foreground_window_change"

    def evaluate(
        self,
        difference: ObservationDifference,
    ) -> list[Finding]:
        """Return findings for foreground-window title changes."""

        findings: list[Finding] = []

        for change in difference.changes:
            if change.path != self.TARGET_PATH:
                continue

            findings.append(
                Finding(
                    title="Foreground application changed",
                    summary=(
                        "The active foreground application or window changed."
                    ),
                    reason=(
                        "The foreground window title changed between "
                        "the previous and current observations."
                    ),
                    confidence=ConfidenceLevel.HIGH,
                    rule_name=self.name,
                    source_path=change.path,
                    before=change.before,
                    after=change.after,
                )
            )

        return findings