"""Tests for Cassandra action selection."""

from __future__ import annotations

import unittest

from cassandra.planner import (
    Action,
    ActionSelector,
    Plan,
)


class ActionSelectorTests(unittest.TestCase):
    """Verify deterministic action selection."""

    def setUp(self) -> None:
        self.selector = ActionSelector()

        self.plan = Plan(
            "Inspect and respond to the environment.",
            "objective_run_test",
        )

    def test_empty_plan_returns_none(self) -> None:
        self.assertIsNone(
            self.selector.select(self.plan)
        )

    def test_first_pending_action_is_selected(self) -> None:
        first = Action(
            "Inspect the environment.",
            "observe",
        )
        second = Action(
            "Generate a response.",
            "generate",
        )

        self.plan.add_action(first)
        self.plan.add_action(second)

        selected = self.selector.select(self.plan)

        self.assertIs(selected, first)

    def test_completed_actions_are_skipped(self) -> None:
        completed = Action(
            "Inspect the environment.",
            "observe",
        )
        completed.activate()
        completed.complete()

        pending = Action(
            "Generate a response.",
            "generate",
        )

        self.plan.add_action(completed)
        self.plan.add_action(pending)

        selected = self.selector.select(self.plan)

        self.assertIs(selected, pending)

    def test_failed_actions_are_skipped(self) -> None:
        failed = Action(
            "Attempt previous strategy.",
            "execute",
        )
        failed.activate()
        failed.fail()

        pending = Action(
            "Attempt another strategy.",
            "execute",
        )

        self.plan.add_action(failed)
        self.plan.add_action(pending)

        selected = self.selector.select(self.plan)

        self.assertIs(selected, pending)

    def test_no_pending_actions_returns_none(self) -> None:
        action = Action(
            "Inspect the environment.",
            "observe",
        )
        action.activate()
        action.complete()

        self.plan.add_action(action)

        self.assertIsNone(
            self.selector.select(self.plan)
        )

    def test_selection_does_not_change_action_state(self) -> None:
        action = Action(
            "Inspect the environment.",
            "observe",
        )

        self.plan.add_action(action)

        selected = self.selector.select(self.plan)

        self.assertIs(selected, action)
        self.assertEqual(action.status, "pending")


if __name__ == "__main__":
    unittest.main()