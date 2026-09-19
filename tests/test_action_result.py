"""Tests for Cassandra execution results."""

from __future__ import annotations

import unittest

from cassandra.execution import ActionResult


class ActionResultTests(unittest.TestCase):
    """Verify execution result behavior."""

    def test_result_preserves_request_id(self) -> None:
        result = ActionResult(
            "request_test",
            True,
        )

        self.assertEqual(
            result.request_id,
            "request_test",
        )

    def test_successful_result_preserves_output(self) -> None:
        result = ActionResult(
            "request_test",
            True,
            output={"code": "candidate_code"},
        )

        self.assertEqual(
            result.output,
            {"code": "candidate_code"},
        )

    def test_failed_result_can_contain_error(self) -> None:
        result = ActionResult(
            "request_test",
            False,
            error="Execution failed.",
        )

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "Execution failed.",
        )

    def test_blank_request_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ActionResult(
                "   ",
                True,
            )

    def test_successful_result_cannot_contain_error(self) -> None:
        with self.assertRaises(ValueError):
            ActionResult(
                "request_test",
                True,
                error="Unexpected error.",
            )

    def test_blank_error_is_normalized_to_none(self) -> None:
        result = ActionResult(
            "request_test",
            False,
            error="   ",
        )

        self.assertIsNone(result.error)

    def test_serialization_preserves_state(self) -> None:
        result = ActionResult(
            "request_test",
            True,
            output={
                "code": "candidate_code",
            },
            metadata={
                "executor": "test",
            },
        )

        serialized = result.to_dict()

        self.assertEqual(
            serialized["request_id"],
            "request_test",
        )
        self.assertTrue(serialized["success"])
        self.assertEqual(
            serialized["output"],
            {"code": "candidate_code"},
        )
        self.assertIsNone(serialized["error"])
        self.assertEqual(
            serialized["metadata"],
            {"executor": "test"},
        )
        self.assertTrue(
            serialized["result_id"].startswith("result_")
        )


if __name__ == "__main__":
    unittest.main()