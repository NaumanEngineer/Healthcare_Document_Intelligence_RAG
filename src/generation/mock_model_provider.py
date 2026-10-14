"""Week 24 Day 3 — deterministic mock model provider."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class DeterministicMockProvider:
    """Return a predefined deterministic model response."""

    provider_name = "deterministic_mock"
    model_name = "week24-test-model"

    def __init__(
        self,
        response: Any,
    ) -> None:
        self._response = deepcopy(
            response
        )

    def generate(
        self,
        prompt: str,
    ) -> Any:
        if (
            not isinstance(
                prompt,
                str,
            )
            or not prompt.strip()
        ):
            raise ValueError(
                "Prompt must be a non-empty string."
            )

        return deepcopy(
            self._response
        )


class ErrorMockProvider:
    """Simulate a provider execution failure."""

    provider_name = "error_mock"
    model_name = "week24-error-model"

    def __init__(
        self,
        message: str = "Simulated provider failure.",
    ) -> None:
        self._message = message

    def generate(
        self,
        prompt: str,
    ) -> Any:
        raise RuntimeError(
            self._message
        )


class FreeTextMockProvider:
    """Simulate a provider returning invalid free-form text."""

    provider_name = "free_text_mock"
    model_name = "week24-free-text-model"

    def __init__(
        self,
        response: str = "This is an unstructured model response.",
    ) -> None:
        self._response = response

    def generate(
        self,
        prompt: str,
    ) -> str:
        return self._response