"""Tests for Week 24 controlled live-provider configuration."""

from __future__ import annotations

import pytest

from src.generation.live_provider_config import (
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT_SECONDS,
    LiveProviderConfig,
    load_api_key,
    safe_config_metadata,
)


def _config() -> LiveProviderConfig:
    return LiveProviderConfig(
        provider_name="test_provider",
        model_name="test_model",
        api_key_env_var="TEST_PROVIDER_API_KEY",
    )


def test_default_configuration_values() -> None:
    config = _config()

    assert (
        config.temperature
        == DEFAULT_TEMPERATURE
    )

    assert (
        config.max_output_tokens
        == DEFAULT_MAX_OUTPUT_TOKENS
    )

    assert (
        config.timeout_seconds
        == DEFAULT_TIMEOUT_SECONDS
    )


def test_api_key_loads_from_supplied_environment() -> None:
    config = _config()

    key = load_api_key(
        config,
        {
            "TEST_PROVIDER_API_KEY": "secret-value",
        },
    )

    assert key == "secret-value"


def test_api_key_is_trimmed() -> None:
    config = _config()

    key = load_api_key(
        config,
        {
            "TEST_PROVIDER_API_KEY": "  secret-value  ",
        },
    )

    assert key == "secret-value"


def test_missing_api_key_fails_closed() -> None:
    config = _config()

    with pytest.raises(
        ValueError,
        match="Missing API key environment variable",
    ):
        load_api_key(
            config,
            {},
        )


def test_blank_api_key_fails_closed() -> None:
    config = _config()

    with pytest.raises(
        ValueError,
        match="Missing API key environment variable",
    ):
        load_api_key(
            config,
            {
                "TEST_PROVIDER_API_KEY": "   ",
            },
        )


def test_safe_metadata_does_not_include_secret_value() -> None:
    config = _config()

    metadata = safe_config_metadata(
        config
    )

    assert (
        metadata["api_key_env_var"]
        == "TEST_PROVIDER_API_KEY"
    )

    assert "api_key" not in metadata
    assert "secret-value" not in metadata.values()


@pytest.mark.parametrize(
    "field,value,error",
    [
        (
            "provider_name",
            "",
            "provider_name must be a non-empty string",
        ),
        (
            "model_name",
            "",
            "model_name must be a non-empty string",
        ),
        (
            "api_key_env_var",
            "",
            "api_key_env_var must be a non-empty string",
        ),
    ],
)
def test_blank_identity_fields_fail_closed(
    field: str,
    value: str,
    error: str,
) -> None:
    kwargs = {
        "provider_name": "provider",
        "model_name": "model",
        "api_key_env_var": "API_KEY",
    }

    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match=error,
    ):
        LiveProviderConfig(
            **kwargs,
        )


@pytest.mark.parametrize(
    "temperature",
    [
        -0.1,
        1.1,
    ],
)
def test_invalid_temperature_fails_closed(
    temperature: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="temperature must be between",
    ):
        LiveProviderConfig(
            provider_name="provider",
            model_name="model",
            api_key_env_var="API_KEY",
            temperature=temperature,
        )


@pytest.mark.parametrize(
    "max_output_tokens",
    [
        0,
        -1,
    ],
)
def test_invalid_token_limit_fails_closed(
    max_output_tokens: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_output_tokens must be greater than zero",
    ):
        LiveProviderConfig(
            provider_name="provider",
            model_name="model",
            api_key_env_var="API_KEY",
            max_output_tokens=max_output_tokens,
        )


@pytest.mark.parametrize(
    "timeout_seconds",
    [
        0,
        -1,
    ],
)
def test_invalid_timeout_fails_closed(
    timeout_seconds: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="timeout_seconds must be greater than zero",
    ):
        LiveProviderConfig(
            provider_name="provider",
            model_name="model",
            api_key_env_var="API_KEY",
            timeout_seconds=timeout_seconds,
        )