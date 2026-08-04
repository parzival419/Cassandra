"""Domain model for Cassandra evaluation results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from cassandra.evaluation.finding import Finding


@dataclass(slots=True)
class EvaluationResult:
    """Represent the complete result of evaluating an observation difference."""

    previous_observation_id: str
    current_observation_id: str
    findings: list[Finding] = field(default_factory=list)
    evaluated_rules: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    evaluation_id: str = field(
        default_factory=lambda: f"evaluation_{uuid4().hex}"
    )
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def has_findings(self) -> bool:
        """Return whether the evaluation produced any findings."""

        return bool(self.findings)

    @property
    def finding_count(self) -> int:
        """Return the number of findings produced."""

        return len(self.findings)

    @property
    def evaluated_rule_count(self) -> int:
        """Return the number of successfully evaluated rules."""

        return len(self.evaluated_rules)

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        data = asdict(self)
        data["findings"] = [
            finding.to_dict()
            for finding in self.findings
        ]
        data["timestamp"] = self.timestamp.isoformat()
        data["has_findings"] = self.has_findings
        data["finding_count"] = self.finding_count
        data["evaluated_rule_count"] = self.evaluated_rule_count

        return data