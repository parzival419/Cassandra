"""Tests for Cassandra executors."""

from __future__ import annotations

import unittest

from cassandra.execution import (
    ActionRequest,
    ActionResult,
    DeterministicExecutor,
    Executor,
)


class DeterministicExecutorTests(unittest.TestCase):
    """Verify deterministic executor behavior."""

    def test_executor_satisfies_protocol(self) -> None:
        executor: Executor = DeterministicExecutor()

        self.assertIsInstance(
            executor,
            DeterministicExecutor,
        )

    def test_execute_returns_action_result(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        result = DeterministicExecutor().execute(request)

        self.assertIsInstance(
            result,
            ActionResult,
        )

    def test_result_is_successful(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        result = DeterministicExecutor().execute(request)

        self.assertTrue(result.success)
        self.assertIsNone(result.error)

    def test_result_preserves_request_id(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        result = DeterministicExecutor().execute(request)

        self.assertEqual(
            result.request_id,
            request.request_id,
        )

    def test_result_contains_instruction(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        result = DeterministicExecutor().execute(request)

        self.assertEqual(
            result.output["instruction"],
            "Inspect the current environment.",
        )

    def test_result_contains_context(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
            context={
                "environment": "development_sandbox",
            },
        )

        result = DeterministicExecutor().execute(request)

        self.assertEqual(
            result.output["context"],
            {
                "environment": "development_sandbox",
            },
        )

    def test_result_identifies_executor(self) -> None:
        request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
        )

        result = DeterministicExecutor().execute(request)

        self.assertEqual(
            result.metadata["executor"],
            "deterministic",
        )


if __name__ == "__main__":
    unittest.main()