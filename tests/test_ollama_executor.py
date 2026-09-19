"""Tests for the Cassandra Ollama executor."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from cassandra.execution import ActionRequest
from cassandra.execution.ollama import OllamaExecutor


class FakeResponse:
    """Provide a minimal HTTP response for executor tests."""

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class OllamaExecutorTests(unittest.TestCase):
    """Verify Ollama-backed execution behavior."""

    def setUp(self) -> None:
        self.executor = OllamaExecutor(
            base_url="http://192.168.1.102:11434",
            model="qwen3:8b",
        )

        self.request = ActionRequest(
            "action_test",
            "Inspect the current environment.",
            context={
                "environment": "development_sandbox",
            },
        )

    @patch("cassandra.execution.ollama.urlopen")
    def test_execute_returns_successful_result(
        self,
        mock_urlopen,
    ) -> None:
        mock_urlopen.return_value = FakeResponse(
            {
                "model": "qwen3:8b",
                "response": "Environment inspected.",
                "thinking": "Internal model reasoning.",
                "done": True,
                "done_reason": "stop",
                "eval_count": 12,
                "eval_duration": 1000,
            }
        )

        result = self.executor.execute(self.request)

        self.assertTrue(result.success)
        self.assertIsNone(result.error)
        self.assertEqual(
            result.request_id,
            self.request.request_id,
        )
        self.assertEqual(
            result.output,
            "Environment inspected.",
        )

    @patch("cassandra.execution.ollama.urlopen")
    def test_result_identifies_ollama_executor(
        self,
        mock_urlopen,
    ) -> None:
        mock_urlopen.return_value = FakeResponse(
            {
                "model": "qwen3:8b",
                "response": "Environment inspected.",
                "done": True,
            }
        )

        result = self.executor.execute(self.request)

        self.assertEqual(
            result.metadata["executor"],
            "ollama",
        )
        self.assertEqual(
            result.metadata["model"],
            "qwen3:8b",
        )

    @patch("cassandra.execution.ollama.urlopen")
    def test_request_contains_instruction_and_context(
        self,
        mock_urlopen,
    ) -> None:
        mock_urlopen.return_value = FakeResponse(
            {
                "model": "qwen3:8b",
                "response": "Environment inspected.",
                "done": True,
            }
        )

        self.executor.execute(self.request)

        http_request = mock_urlopen.call_args.args[0]
        payload = json.loads(
            http_request.data.decode("utf-8")
        )

        self.assertEqual(
            payload["model"],
            "qwen3:8b",
        )
        self.assertFalse(payload["stream"])

        self.assertIn(
            "Inspect the current environment.",
            payload["prompt"],
        )
        self.assertIn(
            "development_sandbox",
            payload["prompt"],
        )

    @patch("cassandra.execution.ollama.urlopen")
    def test_thinking_is_metadata_not_output(
        self,
        mock_urlopen,
    ) -> None:
        mock_urlopen.return_value = FakeResponse(
            {
                "model": "qwen3:8b",
                "response": "Environment inspected.",
                "thinking": "Internal model reasoning.",
                "done": True,
            }
        )

        result = self.executor.execute(self.request)

        self.assertEqual(
            result.output,
            "Environment inspected.",
        )
        self.assertNotIn(
            "thinking",
            result.metadata,
        )


if __name__ == "__main__":
    unittest.main()