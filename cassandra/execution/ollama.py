"""Ollama-backed execution for Cassandra."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cassandra.execution.request import ActionRequest
from cassandra.execution.result import ActionResult


class OllamaExecutor:
    """Execute Cassandra action requests using an Ollama model."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model.strip()
        self.timeout = timeout

        if not self.base_url:
            raise ValueError(
                "OllamaExecutor requires a base URL."
            )

        if not self.model:
            raise ValueError(
                "OllamaExecutor requires a model."
            )

    def execute(
        self,
        request: ActionRequest,
    ) -> ActionResult:
        """Execute an action request through Ollama."""

        payload = {
            "model": self.model,
            "prompt": self._build_prompt(request),
            "stream": False,
        }

        http_request = Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                http_request,
                timeout=self.timeout,
            ) as response:
                response_data: dict[str, Any] = json.loads(
                    response.read().decode("utf-8")
                )

        except (HTTPError, URLError, TimeoutError) as exc:
            return ActionResult(
                request_id=request.request_id,
                success=False,
                error=str(exc),
                metadata={
                    "executor": "ollama",
                    "model": self.model,
                },
            )

        return ActionResult(
            request_id=request.request_id,
            success=True,
            output=response_data.get("response"),
            metadata={
                "executor": "ollama",
                "model": response_data.get(
                    "model",
                    self.model,
                ),
                "done": response_data.get("done"),
                "done_reason": response_data.get(
                    "done_reason"
                ),
                "eval_count": response_data.get(
                    "eval_count"
                ),
                "eval_duration": response_data.get(
                    "eval_duration"
                ),
            },
        )

    @staticmethod
    def _build_prompt(
        request: ActionRequest,
    ) -> str:
        """Build the model prompt from an action request."""

        context = json.dumps(
            request.context,
            indent=2,
            sort_keys=True,
        )

        return (
            "Execute the following Cassandra action.\n\n"
            f"Instruction:\n{request.instruction}\n\n"
            f"Context:\n{context}"
        )