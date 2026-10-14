"""Tests for Week 24 controlled live-model provider adapter."""

from __future__ import annotations

import os

import pytest

from src.generation.live_model_provider import (
    LiveModelProvider,
)
from src.generation.live_provider_config import (
    LiveProviderConfig,
)


def _config() -> LiveProviderConfig:
    return LiveProviderConfig(
        provider_name="test_provider",
        model_name="test_model",
        api_key_env_var="TEST_PROVIDER_API_KEY",
        temperature=0.1,
        max_output_tokens=500,
        timeout_seconds=12.0,
    )


def test_provider_identity_properties() -> None:
    provider = LiveModelProvider(
        _config(),
        lambda *args: {},
    )

    assert (
        provider.provider_name
        == "test_provider"
    )

    assert (
        provider.model_name
        == "test_model"
    )


def test_generate_passes_controlled_configuration_to_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_PROVIDER_API_KEY",
        "secret-key",
    )

    captured = {}

    def transport(
        api_key: str,
        model_name: str,
        prompt: str,
        temperature: float,
        max_output_tokens: int,
        timeout_seconds: float,
    ) -> dict:
        captured.update(
            {
                "api_key": api_key,
                "model_name": model_name,
                "prompt": prompt,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "timeout_seconds": timeout_seconds,
            }
        )

        return {
            "status": "ok",
        }

    provider = LiveModelProvider(
        _config(),
        transport,
    )

    result = provider.generate(
        "Governed prompt"
    )

    assert result == {
        "status": "ok",
    }

    assert (
        captured["api_key"]
        == "secret-key"
    )

    assert (
        captured["model_name"]
        == "test_model"
    )

    assert (
        captured["prompt"]
        == "Governed prompt"
    )

    assert (
        captured["temperature"]
        == 0.1
    )

    assert (
        captured["max_output_tokens"]
        == 500
    )

    assert (
        captured["timeout_seconds"]
        == 12.0
    )


def test_generate_returns_deep_copy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_PROVIDER_API_KEY",
        "secret-key",
    )

    transport_output = {
        "sections": {
            "summary": "Original",
        }
    }

    provider = LiveModelProvider(
        _config(),
        lambda *args: transport_output,
    )

    result = provider.generate(
        "Governed prompt"
    )

    transport_output[
        "sections"
    ][
        "summary"
    ] = "MUTATED"

    assert (
        result["sections"]["summary"]
        == "Original"
    )


@pytest.mark.parametrize(
    "prompt",
    [
        "",
        "   ",
    ],
)
def test_blank_prompt_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    prompt: str,
) -> None:
    monkeypatch.setenv(
        "TEST_PROVIDER_API_KEY",
        "secret-key",
    )

    provider = LiveModelProvider(
        _config(),
        lambda *args: {},
    )

    with pytest.raises(
        ValueError,
        match="prompt must be a non-empty string",
    ):
        provider.generate(
            prompt
        )


def test_missing_api_key_fails_before_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "TEST_PROVIDER_API_KEY",
        raising=False,
    )

    called = False

    def transport(*args):
        nonlocal called
        called = True
        return {}

    provider = LiveModelProvider(
        _config(),
        transport,
    )

    with pytest.raises(
        ValueError,
        match="Missing API key environment variable",
    ):
        provider.generate(
            "Governed prompt"
        )

    assert called is False


def test_transport_failure_propagates_to_execution_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_PROVIDER_API_KEY",
        "secret-key",
    )

    def failing_transport(*args):
        raise RuntimeError(
            "Simulated provider failure."
        )

    provider = LiveModelProvider(
        _config(),
        failing_transport,
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated provider failure",
    ):
        provider.generate(
            "Governed prompt"
        )


def test_non_callable_transport_fails_closed() -> None:
    with pytest.raises(
        ValueError,
        match="transport must be callable",
    ):
        LiveModelProvider(
            _config(),
            None,  # type: ignore[arg-type]
        )


def test_environment_value_is_not_stored_on_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_PROVIDER_API_KEY",
        "secret-key",
    )

    provider = LiveModelProvider(
        _config(),
        lambda *args: {},
    )

    provider.generate(
        "Governed prompt"
    )

    assert not hasattr(
        provider,
        "api_key",
    )

    assert "secret-key" not in str(
        provider.__dict__
    )