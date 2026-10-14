"""Week 24 Day 5 — controlled live-provider configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_OUTPUT_TOKENS = 800
DEFAULT_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class LiveProviderConfig:
    """Configuration for a controlled live model provider."""

    provider_name: str
    model_name: str
    api_key_env_var: str
    temperature: float = DEFAULT_TEMPERATURE
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if not self.provider_name.strip():
            raise ValueError(
                "provider_name must be a non-empty string."
            )

        if not self.model_name.strip():
            raise ValueError(
                "model_name must be a non-empty string."
            )

        if not self.api_key_env_var.strip():
            raise ValueError(
                "api_key_env_var must be a non-empty string."
            )

        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError(
                "temperature must be between 0.0 and 1.0."
            )

        if self.max_output_tokens <= 0:
            raise ValueError(
                "max_output_tokens must be greater than zero."
            )

        if self.timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )


def load_api_key(
    config: LiveProviderConfig,
    environment: Mapping[str, str] | None = None,
) -> str:
    """Load provider API key from environment without exposing it."""

    source = os.environ if environment is None else environment

    api_key = source.get(
        config.api_key_env_var,
        "",
    )

    if not isinstance(
        api_key,
        str,
    ) or not api_key.strip():
        raise ValueError(
            f"Missing API key environment variable: "
            f"{config.api_key_env_var}"
        )

    return api_key.strip()


def safe_config_metadata(
    config: LiveProviderConfig,
) -> dict:
    """Return non-secret provider configuration metadata."""

    return {
        "provider_name": config.provider_name,
        "model_name": config.model_name,
        "api_key_env_var": config.api_key_env_var,
        "temperature": config.temperature,
        "max_output_tokens": config.max_output_tokens,
        "timeout_seconds": config.timeout_seconds,
    }