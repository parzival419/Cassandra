"""Tests for Cassandra planner plans."""

from __future__ import annotations

import unittest

from cassandra.planner import Action, Plan


class PlanTests(unittest.TestCase):
    """Verify planner plan behavior."""

    def test_plan_starts_pending(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        self.assertEqual(plan.status, "pending")

    def test_plan_starts_with_empty_actions(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        self.assertEqual(plan.actions, [])

    def test_action_can_be_added(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        action = Action(
            "Capture the current state.",
            "observe",
        )

        plan.add_action(action)

        self.assertEqual(len(plan.actions), 1)
        self.assertIs(plan.actions[0], action)

    def test_actions_preserve_order(self) -> None:
        plan = Plan(
            "Inspect and respond to the environment.",
            "objective_run_test",
        )

        first = Action(
            "Inspect the current environment.",
            "observe",
        )
        second = Action(
            "Generate a candidate response.",
            "generate",
        )

        plan.add_action(first)
        plan.add_action(second)

        self.assertEqual(
            plan.actions,
            [first, second],
        )

    def test_pending_plan_can_activate(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        plan.activate()

        self.assertEqual(plan.status, "active")

    def test_active_plan_can_complete(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        plan.activate()
        plan.complete()

        self.assertEqual(plan.status, "completed")

    def test_active_plan_can_fail(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        plan.activate()
        plan.fail()

        self.assertEqual(plan.status, "failed")

    def test_pending_plan_cannot_complete(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        with self.assertRaises(ValueError):
            plan.complete()

    def test_pending_plan_cannot_fail(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        with self.assertRaises(ValueError):
            plan.fail()

    def test_completed_plan_cannot_reactivate(self) -> None:
        plan = Plan(
            "Inspect the environment.",
            "objective_run_test",
        )

        plan.activate()
        plan.complete()

        with self.assertRaises(ValueError):
            plan.activate()

    def test_blank_description_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Plan(
                "   ",
                "objective_run_test",
            )

    def test_blank_objective_run_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Plan(
                "Inspect the environment.",
                "   ",
            )

    def test_invalid_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Plan(
                "Inspect the environment.",
                "objective_run_test",
                status="unknown",
            )

    def test_serialization_includes_actions(self) -> None:
        plan = Plan(
            "Inspect and respond to the environment.",
            "objective_run_test",
            metadata={"source": "planner"},
        )

        plan.add_action(
            Action(
                "Inspect the current environment.",
                "observe",
            )
        )

        result = plan.to_dict()

        self.assertEqual(
            result["description"],
            "Inspect and respond to the environment.",
        )
        self.assertEqual(
            result["objective_run_id"],
            "objective_run_test",
        )
        self.assertEqual(result["status"], "pending")
        self.assertEqual(len(result["actions"]), 1)
        self.assertEqual(
            result["actions"][0]["action_type"],
            "observe",
        )
        self.assertEqual(
            result["metadata"],
            {"source": "planner"},
        )
        self.assertTrue(
            result["plan_id"].startswith("plan_")
        )


if __name__ == "__main__":
    unittest.main()