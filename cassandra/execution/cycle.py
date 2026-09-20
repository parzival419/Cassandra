"""Execution cycle coordination for Cassandra."""

from __future__ import annotations

from cassandra.execution.builder import ActionRequestBuilder
from cassandra.execution.executor import Executor
from cassandra.execution.result import ActionResult
from cassandra.planner import (
    ActionSelector,
    CurrentObjective,
    Plan,
)


class ExecutionCycle:
    """Coordinate execution of one pending plan action."""

    def __init__(
        self,
        action_selector: ActionSelector,
        request_builder: ActionRequestBuilder,
        executor: Executor,
    ) -> None:
        self.action_selector = action_selector
        self.request_builder = request_builder
        self.executor = executor

    def execute(
        self,
        plan: Plan,
        objective: CurrentObjective,
        experiment_instructions: str,
        observation: str,
    ) -> ActionResult | None:
        """Execute the next pending action in a plan."""

        action = self.action_selector.select(plan)

        if action is None:
            return None

        action.activate()

        request = self.request_builder.build(
            action=action,
            objective=objective,
            experiment_instructions=experiment_instructions,
            observation=observation,
        )

        return self.executor.execute(request)