"""Tests for document dirty-state evaluation."""

from __future__ import annotations

import unittest

from cassandra.evaluation.rules import DocumentDirtyStateRule
from cassandra.observation.comparison import (
    FieldChange,
    ObservationDifference,
)


class DocumentDirtyStateRuleTests(unittest.TestCase):
    """Verify document dirty-state transitions."""

    def setUp(self) -> None:
        self.rule = DocumentDirtyStateRule()

    def _difference(
        self,
        before: bool,
        after: bool,
    ) -> ObservationDifference:
        return ObservationDifference(
            previous_observation_id="obs_previous",
            current_observation_id="obs_current",
            changes=[
                FieldChange(
                    path="state.window.normalized.is_dirty",
                    before=before,
                    after=after,
                ),
            ],
        )

    def test_clean_to_dirty_produces_modified_finding(
        self,
    ) -> None:
        difference = self._difference(
            before=False,
            after=True,
        )

        findings = self.rule.evaluate(difference)

        self.assertEqual(len(findings), 1)

        finding = findings[0]

        self.assertEqual(
            finding.title,
            "Document modified",
        )
        self.assertEqual(
            finding.rule_name,
            "document_dirty_state",
        )
        self.assertFalse(finding.before)
        self.assertTrue(finding.after)

    def test_dirty_to_clean_produces_saved_finding(
        self,
    ) -> None:
        difference = self._difference(
            before=True,
            after=False,
        )

        findings = self.rule.evaluate(difference)

        self.assertEqual(len(findings), 1)

        finding = findings[0]

        self.assertEqual(
            finding.title,
            "Document saved",
        )
        self.assertEqual(
            finding.rule_name,
            "document_dirty_state",
        )
        self.assertTrue(finding.before)
        self.assertFalse(finding.after)

    def test_clean_to_clean_produces_no_finding(
        self,
    ) -> None:
        difference = self._difference(
            before=False,
            after=False,
        )

        findings = self.rule.evaluate(difference)

        self.assertEqual(findings, [])

    def test_dirty_to_dirty_produces_no_finding(
        self,
    ) -> None:
        difference = self._difference(
            before=True,
            after=True,
        )

        findings = self.rule.evaluate(difference)

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()