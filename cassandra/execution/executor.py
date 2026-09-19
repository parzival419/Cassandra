"""Execution interfaces and deterministic executors for Cassandra."""

from __future__ import annotations

from typing import Protocol

from cassandra.execution.request import ActionRequest
from cassandra.execution.result import ActionResult


class Executor(Protocol):
    """Define the contract for Cassandra action executors."""

    def execute(
        self,
        request: ActionRequest,
    ) -> ActionResult:
        """Execute an action request and return its result."""
        ...


class DeterministicExecutor:
    """Execute requests predictably for testing and development."""

    def execute(
        self,
        request: ActionRequest,
    ) -> ActionResult:
        """Return a deterministic successful result."""

        return ActionResult(
            request_id=request.request_id,
            success=True,
            output={
                "instruction": request.instruction,
                "context": request.context,
            },
            metadata={
                "executor": "deterministic",
            },
        )