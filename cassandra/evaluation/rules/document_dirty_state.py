"""Evaluate document dirty-state transitions."""

from __future__ import annotations

from cassandra.evaluation.finding import (
    ConfidenceLevel,
    Finding,
)
from cassandra.evaluation.rule import EvaluationRule
from cassandra.observation.comparison import (
    FieldChange,
    ObservationDifference,
)


class DocumentDirtyStateRule(EvaluationRule):
    """Detect document modification and save transitions."""

    SOURCE_PATH = "state.window.normalized.is_dirty"

    @property
    def name(self) -> str:
        """Return the rule name."""

        return "document_dirty_state"

    def evaluate(
        self,
        difference: ObservationDifference,
    ) -> list[Finding]:
        """Evaluate dirty-state changes."""

        findings: list[Finding] = []

        for change in difference.changes:
            if change.path != self.SOURCE_PATH:
                continue

            finding = self._build_finding(change)

            if finding is not None:
                findings.append(finding)

        return findings

    def _build_finding(
        self,
        change: FieldChange,
    ) -> Finding | None:
        """Build a finding from a dirty-state transition."""

        if change.before is False and change.after is True:
            return Finding(
                title="Document modified",
                summary=(
                    "The active document entered an unsaved state."
                ),
                reason=(
                    "The normalized VS Code document dirty state "
                    "changed from clean to dirty."
                ),
                confidence=ConfidenceLevel.HIGH,
                rule_name=self.name,
                source_path=self.SOURCE_PATH,
                before=change.before,
                after=change.after,
            )

        if change.before is True and change.after is False:
            return Finding(
                title="Document saved",
                summary=(
                    "The active document returned to a saved state."
                ),
                reason=(
                    "The normalized VS Code document dirty state "
                    "changed from dirty to clean."
                ),
                confidence=ConfidenceLevel.HIGH,
                rule_name=self.name,
                source_path=self.SOURCE_PATH,
                before=change.before,
                after=change.after,
            )

        return None