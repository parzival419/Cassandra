"""Tests for Cassandra planner actions."""

from __future__ import annotations

import unittest

from cassandra.planner import Action


class ActionTests(unittest.TestCase):
    """Verify planner action behavior."""

    def test_action_starts_pending(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        self.assertEqual(action.status, "pending")

    def test_pending_action_can_activate(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        action.activate()

        self.assertEqual(action.status, "active")

    def test_active_action_can_complete(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        action.activate()
        action.complete()

        self.assertEqual(action.status, "completed")

    def test_active_action_can_fail(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        action.activate()
        action.fail()

        self.assertEqual(action.status, "failed")

    def test_pending_action_cannot_complete(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        with self.assertRaises(ValueError):
            action.complete()

    def test_pending_action_cannot_fail(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        with self.assertRaises(ValueError):
            action.fail()

    def test_completed_action_cannot_reactivate(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "observe",
        )

        action.activate()
        action.complete()

        with self.assertRaises(ValueError):
            action.activate()

    def test_blank_description_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Action(
                "   ",
                "observe",
            )

    def test_blank_action_type_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Action(
                "Inspect the current environment.",
                "   ",
            )

    def test_invalid_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Action(
                "Inspect the current environment.",
                "observe",
                status="unknown",
            )

    def test_serialization_preserves_state(self) -> None:
        action = Action(
            "Inspect the current environment.",
            "Observe",
            metadata={"source": "planner"},
        )

        result = action.to_dict()

        self.assertEqual(
            result["description"],
            "Inspect the current environment.",
        )
        self.assertEqual(result["action_type"], "observe")
        self.assertEqual(result["status"], "pending")
        self.assertEqual(
            result["metadata"],
            {"source": "planner"},
        )
        self.assertTrue(
            result["action_id"].startswith("action_")
        )


if __name__ == "__main__":
    unittest.main()