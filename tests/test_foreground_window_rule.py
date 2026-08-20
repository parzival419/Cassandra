"""Tests for foreground-window evaluation."""

from __future__ import annotations

import unittest

from cassandra.evaluation.rules import ForegroundWindowRule
from cassandra.observation.comparison import (
    FieldChange,
    ObservationDifference,
)


class ForegroundWindowRuleTests(unittest.TestCase):
    """Verify foreground-application change evaluation."""

    def setUp(self) -> None:
        self.rule = ForegroundWindowRule()

    def _difference(
        self,
        before: object,
        after: object,
        path: str = "state.window.normalized.application",
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

    def test_application_change_produces_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="Visual Studio Code",
                after="Microsoft Edge",
            )
        )

        self.assertEqual(len(findings), 1)

        finding = findings[0]

        self.assertEqual(
            finding.title,
            "Foreground application changed",
        )
        self.assertEqual(
            finding.rule_name,
            "foreground_application_change",
        )
        self.assertEqual(
            finding.before,
            "Visual Studio Code",
        )
        self.assertEqual(
            finding.after,
            "Microsoft Edge",
        )

    def test_none_before_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before=None,
                after="Visual Studio Code",
            )
        )

        self.assertEqual(findings, [])

    def test_none_after_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="Visual Studio Code",
                after=None,
            )
        )

        self.assertEqual(findings, [])

    def test_unrelated_path_produces_no_finding(self) -> None:
        findings = self.rule.evaluate(
            self._difference(
                before="a.py",
                after="b.py",
                path="state.window.normalized.document",
            )
        )

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()