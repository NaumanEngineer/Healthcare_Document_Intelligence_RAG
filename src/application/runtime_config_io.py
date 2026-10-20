"""Week 27 Day 3 — safe runtime configuration loading and serialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.application.runtime_config import (
    AssurancePolicy,
    RAGRuntimeConfig,
    RetrievalConfig,
    RuntimeMetadata,
)


_ALLOWED_TOP_LEVEL_KEYS = {
    "execution_mode",
    "retrieval",
    "assurance",
    "metadata",
}

_FORBIDDEN_KEY_FRAGMENTS = {
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "credential",
    "authorization",
    "bearer",
}


def _require_mapping(
    value: Any,
    name: str,
) -> dict:
    if not isinstance(value, dict):
        raise ValueError(
            f"{name} must be a dictionary."
        )

    return value


def _reject_forbidden_keys(
    value: Any,
    *,
    path: str = "config",
) -> None:
    """Reject likely secret-bearing configuration fields recursively."""

    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"{path} keys must be strings."
                )

            normalized = key.lower().replace("-", "_")

            if any(
                fragment in normalized
                for fragment in _FORBIDDEN_KEY_FRAGMENTS
            ):
                raise ValueError(
                    f"Forbidden sensitive configuration key: "
                    f"{path}.{key}"
                )

            _reject_forbidden_keys(
                child,
                path=f"{path}.{key}",
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_keys(
                child,
                path=f"{path}[{index}]",
            )


def runtime_config_from_dict(
    payload: dict,
) -> RAGRuntimeConfig:
    """Build validated runtime configuration from a plain dictionary."""

    payload = _require_mapping(
        payload,
        "runtime configuration",
    )

    _reject_forbidden_keys(
        payload
    )

    unknown = (
        set(payload)
        - _ALLOWED_TOP_LEVEL_KEYS
    )

    if unknown:
        raise ValueError(
            "Unknown runtime configuration keys: "
            + ", ".join(
                sorted(
                    unknown
                )
            )
        )

    retrieval_payload = _require_mapping(
        payload.get(
            "retrieval",
            {},
        ),
        "retrieval",
    )

    assurance_payload = _require_mapping(
        payload.get(
            "assurance",
            {},
        ),
        "assurance",
    )

    metadata_payload = _require_mapping(
        payload.get(
            "metadata",
            {},
        ),
        "metadata",
    )

    execution_mode = payload.get(
        "execution_mode",
        "DETERMINISTIC_ONLY",
    )

    return RAGRuntimeConfig(
        retrieval=RetrievalConfig(
            **retrieval_payload
        ),
        assurance=AssurancePolicy(
            **assurance_payload
        ),
        metadata=RuntimeMetadata(
            **metadata_payload
        ),
        execution_mode=execution_mode,
    )


def load_runtime_config(
    path: str | Path,
) -> RAGRuntimeConfig:
    """Load and validate a JSON runtime configuration file."""

    config_path = Path(
        path
    )

    if not config_path.exists():
        raise ValueError(
            f"Runtime configuration file does not exist: "
            f"{config_path}"
        )

    if not config_path.is_file():
        raise ValueError(
            f"Runtime configuration path is not a file: "
            f"{config_path}"
        )

    if config_path.suffix.lower() != ".json":
        raise ValueError(
            "Runtime configuration file must use .json."
        )

    try:
        raw_text = config_path.read_text(
            encoding="utf-8"
        )
    except Exception as exc:
        raise ValueError(
            "Unable to read runtime configuration file."
        ) from exc

    try:
        payload = json.loads(
            raw_text
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Runtime configuration file contains invalid JSON."
        ) from exc

    return runtime_config_from_dict(
        payload
    )


def save_runtime_config(
    config: RAGRuntimeConfig,
    path: str | Path,
) -> Path:
    """Write a validated non-sensitive runtime configuration to JSON."""

    if not isinstance(
        config,
        RAGRuntimeConfig,
    ):
        raise ValueError(
            "config must be a RAGRuntimeConfig."
        )

    payload = config.to_dict()

    _reject_forbidden_keys(
        payload
    )

    config_path = Path(
        path
    )

    if config_path.suffix.lower() != ".json":
        raise ValueError(
            "Runtime configuration file must use .json."
        )

    config_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    config_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return config_path