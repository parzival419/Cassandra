"""Rule for interpreting active-document changes."""

from __future__ import annotations

from cassandra.evaluation.finding import (
    ConfidenceLevel,
    Finding,
)
from cassandra.evaluation.rule import EvaluationRule
from cassandra.observation.comparison import ObservationDifference


class ActiveDocumentRule(EvaluationRule):
    """Interpret a change to the normalized active document."""

    TARGET_PATH = "state.window.normalized.document"

    @property
    def name(self) -> str:
        """Return the rule's stable identifier."""

        return "active_document_change"

    def evaluate(
        self,
        difference: ObservationDifference,
    ) -> list[Finding]:
        """Return findings for active-document changes."""

        findings: list[Finding] = []

        for change in difference.changes:
            if change.path != self.TARGET_PATH:
                continue

            if not isinstance(change.before, str):
                continue

            if not isinstance(change.after, str):
                continue

            if not change.before.strip() or not change.after.strip():
                continue

            findings.append(
                Finding(
                    title="Active document changed",
                    summary=(
                        "The active document changed within the "
                        "foreground application."
                    ),
                    reason=(
                        "The normalized document field differed between "
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