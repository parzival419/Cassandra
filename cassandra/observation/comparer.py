"""Compare Cassandra observation dictionaries."""

from __future__ import annotations

from typing import Any

from cassandra.observation.comparison import (
    FieldChange,
    ObservationDifference,
)


class ObservationComparer:
    """Compare two persisted observation dictionaries."""

    IGNORED_PATHS = {
        "observation_id",
        "timestamp",
        "metadata.duration_ms",
    }

    def compare(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
    ) -> ObservationDifference:
        """Return the structured differences between two observations."""

        previous_id = self._get_observation_id(previous, "previous")
        current_id = self._get_observation_id(current, "current")

        changes: list[FieldChange] = []

        self._compare_values(
            previous,
            current,
            path="",
            changes=changes,
        )

        return ObservationDifference(
            previous_observation_id=previous_id,
            current_observation_id=current_id,
            changes=changes,
        )

    def _compare_values(
        self,
        previous: Any,
        current: Any,
        path: str,
        changes: list[FieldChange],
    ) -> None:
        """Recursively compare two values."""

        if isinstance(previous, dict) and isinstance(current, dict):
            self._compare_dictionaries(
                previous,
                current,
                path,
                changes,
            )
            return

        if isinstance(previous, list) and isinstance(current, list):
            self._compare_lists(
                previous,
                current,
                path,
                changes,
            )
            return

        if previous != current:
            current_path = path or "<root>"

            if self._should_ignore(current_path):
                return

            changes.append(
                FieldChange(
                    path=current_path,
                    before=previous,
                    after=current,
                )
            )

    def _compare_dictionaries(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
        path: str,
        changes: list[FieldChange],
    ) -> None:
        """Compare dictionaries by key."""

        keys = sorted(set(previous) | set(current))

        for key in keys:
            child_path = f"{path}.{key}" if path else key

            if key not in previous:
                if self._should_ignore(child_path):
                    continue

                changes.append(
                    FieldChange(
                        path=child_path,
                        before=None,
                        after=current[key],
                    )
                )
                continue

            if key not in current:
                if self._should_ignore(child_path):
                    continue

                changes.append(
                    FieldChange(
                        path=child_path,
                        before=previous[key],
                        after=None,
                    )
                )
                continue

            self._compare_values(
                previous[key],
                current[key],
                child_path,
                changes,
            )

    def _compare_lists(
        self,
        previous: list[Any],
        current: list[Any],
        path: str,
        changes: list[FieldChange],
    ) -> None:
        """Compare list values by position."""

        max_length = max(len(previous), len(current))

        for index in range(max_length):
            child_path = f"{path}[{index}]"

            if index >= len(previous):
                changes.append(
                    FieldChange(
                        path=child_path,
                        before=None,
                        after=current[index],
                    )
                )
                continue

            if index >= len(current):
                changes.append(
                    FieldChange(
                        path=child_path,
                        before=previous[index],
                        after=None,
                    )
                )
                continue

            self._compare_values(
                previous[index],
                current[index],
                child_path,
                changes,
            )

    def _should_ignore(self, path: str) -> bool:
        """Return whether a path should be ignored."""

        return path in self.IGNORED_PATHS

    def _get_observation_id(
        self,
        observation: dict[str, Any],
        label: str,
    ) -> str:
        """Return and validate an observation identifier."""

        observation_id = observation.get("observation_id")

        if not isinstance(observation_id, str):
            raise ValueError(
                f"The {label} observation is missing a valid "
                "'observation_id'."
            )

        return observation_id