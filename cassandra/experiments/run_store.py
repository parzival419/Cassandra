"""Persistent storage for Cassandra experiment runs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from cassandra.experiments.run import ExperimentRun
from cassandra.planner import Action, CurrentObjective, Plan


class ExperimentRunStore:
    """Persist and restore Cassandra experiment runs."""

    def __init__(
        self,
        root: str | Path = "artifacts/experiments",
    ) -> None:
        self.root = Path(root)

    def save(self, run: ExperimentRun) -> Path:
        """Persist an experiment run as JSON."""

        directory = (
            self.root
            / run.experiment_id
            / "runs"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = directory / f"{run.run_id}.json"

        path.write_text(
            json.dumps(
                run.to_dict(),
                indent=2,
            ),
            encoding="utf-8",
        )

        return path

    def load(
        self,
        experiment_id: str,
        run_id: str,
    ) -> ExperimentRun:
        """Load an experiment run from disk."""

        path = (
            self.root
            / experiment_id
            / "runs"
            / f"{run_id}.json"
        )

        if not path.exists():
            raise FileNotFoundError(path)

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        return self._from_dict(data)

    def _from_dict(
        self,
        data: dict[str, Any],
    ) -> ExperimentRun:
        """Reconstruct an ExperimentRun from serialized state."""

        objective = self._objective_from_dict(
            data.get("current_objective")
        )

        plan = self._plan_from_dict(
            data.get("current_plan")
        )

        return ExperimentRun(
            experiment_id=data["experiment_id"],
            current_objective=objective,
            current_plan=plan,
            status=data["status"],
            run_id=data["run_id"],
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data["started_at"]
                else None
            ),
            updated_at=datetime.fromisoformat(
                data["updated_at"]
            ),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def _objective_from_dict(
        data: dict[str, Any] | None,
    ) -> CurrentObjective | None:
        """Reconstruct the current objective."""

        if data is None:
            return None

        return CurrentObjective(
            description=data["description"],
            source_objective_id=data["source_objective_id"],
            status=data["status"],
            objective_run_id=data["objective_run_id"],
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def _plan_from_dict(
        data: dict[str, Any] | None,
    ) -> Plan | None:
        """Reconstruct the current plan and its actions."""

        if data is None:
            return None

        actions = [
            Action(
                description=action["description"],
                action_type=action["action_type"],
                status=action["status"],
                action_id=action["action_id"],
                metadata=action.get("metadata", {}),
            )
            for action in data.get("actions", [])
        ]

        return Plan(
            description=data["description"],
            objective_run_id=data["objective_run_id"],
            actions=actions,
            status=data["status"],
            plan_id=data["plan_id"],
            metadata=data.get("metadata", {}),
        )