"""Tests for Cassandra execution requests."""

from __future__ import annotations

import unittest

from cassandra.execution import ActionRequest


class ActionRequestTests(unittest.TestCase):
    """Verify execution request behavior."""

    def test_request_preserves_action_id(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        self.assertEqual(
            request.action_id,
            "action_test",
        )

    def test_request_preserves_instruction(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        self.assertEqual(
            request.instruction,
            "Inspect the current environment.",
        )

    def test_request_starts_with_empty_context(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        self.assertEqual(request.context, {})

    def test_blank_action_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ActionRequest(
                "   ",
                "Inspect the current environment.",
            )

    def test_blank_instruction_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ActionRequest(
                "action_test",
                "   ",
            )

    def test_values_are_normalized(self) -> None:
        request = ActionRequest(
            "  action_test  ",
            "  Inspect the current environment.  ",
        )

        self.assertEqual(
            request.action_id,
            "action_test",
        )
        self.assertEqual(
            request.instruction,
            "Inspect the current environment.",
        )

    def test_serialization_preserves_context(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
            context={
                "environment": "development_sandbox",
            },
            metadata={
                "source": "planner",
            },
        )

        result = request.to_dict()

        self.assertEqual(
            result["action_id"],
            "action_test",
        )
        self.assertEqual(
            result["context"]["environment"],
            "development_sandbox",
        )
        self.assertEqual(
            result["metadata"],
            {"source": "planner"},
        )
        self.assertTrue(
            result["request_id"].startswith("request_")
        )


if __name__ == "__main__":
    unittest.main()