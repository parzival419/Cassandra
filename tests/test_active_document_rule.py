"""Tests for active-document evaluation."""

from __future__ import annotations

import unittest

from cassandra.evaluation.rules import ActiveDocumentRule
from cassandra.observation.comparison import (
    FieldChange,
    ObservationDifference,
)


class ActiveDocumentRuleTests(unittest.TestCase):
    """Verify active-document change evaluation."""

    def setUp(self) -> None:
        self.rule = ActiveDocumentRule()

    def _difference(
        self,
        before: object,
        after: object,
        path: str = "state.window.normalized.document",
    ) -> ObservationDifference:
        return ObservationDifference(
            previous_observation_id="obs_previous",
            current_observation_id="obs_current",
            changes=[
                FieldChange(
                    path=path,
                    before=before,
                    after=after,
                ),
            ],
        )

    def test_document_change_produces_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="main.py",
                after="README.md",
            )
        )

        self.assertEqual(len(findings), 1)

        finding = findings[0]

        self.assertEqual(
            finding.title,
            "Active document changed",
        )
        self.assertEqual(
            finding.rule_name,
            "active_document_change",
        )
        self.assertEqual(
            finding.before,
            "main.py",
        )
        self.assertEqual(
            finding.after,
            "README.md",
        )

    def test_none_before_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before=None,
                after="README.md",
            )
        )

        self.assertEqual(findings, [])

    def test_none_after_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="main.py",
                after=None,
            )
        )

        self.assertEqual(findings, [])

    def test_blank_document_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="main.py",
                after="   ",
            )
        )

        self.assertEqual(findings, [])

    def test_unrelated_path_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="Visual Studio Code",
                after="Microsoft Edge",
                path="state.window.normalized.application",
            )
        )

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()