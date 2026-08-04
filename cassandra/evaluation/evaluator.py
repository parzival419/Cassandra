"""Coordinate evaluation rules and produce structured results."""

from __future__ import annotations

from collections.abc import Iterable
from time import perf_counter
from typing import Any

from cassandra.evaluation.finding import Finding
from cassandra.evaluation.result import EvaluationResult
from cassandra.evaluation.rule import EvaluationRule
from cassandra.observation.comparison import ObservationDifference


class EvaluationEngine:
    """Run evaluation rules against an observation difference."""

    def __init__(
        self,
        rules: Iterable[EvaluationRule] | None = None,
    ) -> None:
        self._rules = tuple(rules or ())

        self._validate_rule_names()

    def evaluate(
        self,
        difference: ObservationDifference,
    ) -> EvaluationResult:
        """Evaluate a difference and return a structured result."""

        started_at = perf_counter()

        findings: list[Finding] = []
        evaluated_rules: list[str] = []
        rule_errors: dict[str, dict[str, str]] = {}

        for rule in self._rules:
            try:
                findings.extend(
                    rule.evaluate(difference)
                )
                evaluated_rules.append(rule.name)

            except Exception as exc:
                rule_errors[rule.name] = {
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }

        duration_ms = round(
            (perf_counter() - started_at) * 1000,
            3,
        )

        status = (
            "evaluation completed"
            if not rule_errors
            else "evaluation completed with rule errors"
        )

        metadata: dict[str, Any] = {
            "status": status,
            "duration_ms": duration_ms,
            "configured_rule_count": len(self._rules),
            "successful_rule_count": len(evaluated_rules),
            "failed_rule_count": len(rule_errors),
            "finding_count": len(findings),
        }

        if rule_errors:
            metadata["rule_errors"] = rule_errors

        return EvaluationResult(
            previous_observation_id=(
                difference.previous_observation_id
            ),
            current_observation_id=(
                difference.current_observation_id
            ),
            findings=findings,
            evaluated_rules=evaluated_rules,
            metadata=metadata,
        )

    def _validate_rule_names(self) -> None:
        """Reject duplicate evaluation-rule identifiers."""

        rule_names = [
            rule.name
            for rule in self._rules
        ]

        duplicate_names = {
            name
            for name in rule_names
            if rule_names.count(name) > 1
        }

        if duplicate_names:
            duplicates = ", ".join(
                sorted(duplicate_names)
            )

            raise ValueError(
                "Duplicate evaluation rule names are not allowed: "
                f"{duplicates}"
            )