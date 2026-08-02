"""Format observation differences for human-readable output."""

from __future__ import annotations

import json
from typing import Any

from cassandra.observation.comparison import (
    FieldChange,
    ObservationDifference,
)


class ObservationDifferenceFormatter:
    """Format structured observation differences as readable text."""

    def format(self, difference: ObservationDifference) -> str:
        """Return a human-readable comparison report."""

        lines = [
            "Observation Change Report",
            "=" * 25,
            "",
            f"Previous: {difference.previous_observation_id}",
            f"Current : {difference.current_observation_id}",
            "",
        ]

        if not difference.has_changes:
            lines.append("No meaningful changes detected.")
            return "\n".join(lines)

        lines.extend(
            [
                f"Changes detected: {difference.change_count}",
                "",
            ]
        )

        for index, change in enumerate(
            difference.changes,
            start=1,
        ):
            lines.extend(
                self._format_change(
                    index=index,
                    change=change,
                )
            )

        return "\n".join(lines).rstrip()

    def _format_change(
        self,
        index: int,
        change: FieldChange,
    ) -> list[str]:
        """Format one changed field."""

        return [
            f"{index}. {change.path}",
            f"   Before: {self._format_value(change.before)}",
            f"   After : {self._format_value(change.after)}",
            "",
        ]

    def _format_value(self, value: Any) -> str:
        """Return a compact printable representation of a value."""

        if value is None:
            return "<none>"

        if isinstance(value, str):
            return value

        if isinstance(value, (dict, list)):
            return json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
            )

        return str(value)