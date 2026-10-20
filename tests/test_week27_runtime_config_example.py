from pathlib import Path

from src.application.runtime_config import (
    DETERMINISTIC_ONLY,
)
from src.application.runtime_config_io import (
    load_runtime_config,
)


ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = (
    ROOT
    / "config"
    / "runtime_config.example.json"
)


def test_checked_in_runtime_config_example_loads():
    config = load_runtime_config(
        CONFIG_PATH
    )

    assert (
        config.execution_mode
        == DETERMINISTIC_ONLY
    )

    assert (
        config.assurance.require_citation_assurance
        is True
    )

    assert (
        config.assurance.require_faithfulness_assurance
        is True
    )

    assert (
        config.assurance.require_system_safety
        is True
    )

    assert (
        config.assurance.require_prompt_injection_check
        is True
    )


def test_checked_in_runtime_config_contains_no_secrets():
    text = CONFIG_PATH.read_text(
        encoding="utf-8"
    ).lower()

    forbidden = (
        "api_key",
        "password",
        "client_secret",
        "access_token",
        "bearer",
        "credential",
    )

    for term in forbidden:
        assert term not in text