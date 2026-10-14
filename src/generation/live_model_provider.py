"""Week 24 Day 5 — controlled live-model provider adapter."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from src.generation.live_provider_config import (
    LiveProviderConfig,
    load_api_key,
)


ProviderTransport = Callable[
    [
        str,
        str,
        str,
        float,
        int,
        float,
    ],
    Any,
]


class LiveModelProvider:
    """Provider-neutral adapter for controlled live model execution."""

    def __init__(
        self,
        config: LiveProviderConfig,
        transport: ProviderTransport,
    ) -> None:
        if not callable(transport):
            raise ValueError(
                "transport must be callable."
            )

        self._config = config
        self._transport = transport

    @property
    def provider_name(self) -> str:
        return self._config.provider_name

    @property
    def model_name(self) -> str:
        return self._config.model_name

    def generate(
        self,
        prompt: str,
    ) -> Any:
        """Execute one controlled provider request."""

        if (
            not isinstance(
                prompt,
                str,
            )
            or not prompt.strip()
        ):
            raise ValueError(
                "prompt must be a non-empty string."
            )

        api_key = load_api_key(
            self._config
        )

        result = self._transport(
            api_key,
            self._config.model_name,
            prompt,
            self._config.temperature,
            self._config.max_output_tokens,
            self._config.timeout_seconds,
        )

        return deepcopy(
            result
        )