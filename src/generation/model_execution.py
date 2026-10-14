"""Week 24 Day 3 — provider-neutral controlled model execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.generation.controlled_model_generation import (
    validate_model_generation_output,
)
from src.generation.governed_prompt import (
    build_governed_prompt,
)


EXECUTION_ACCEPTED = "ACCEPTED"
EXECUTION_REJECTED = "REJECTED"
EXECUTION_FAILED = "FAILED"

PROVIDER_ERROR = "PROVIDER_ERROR"
PARSE_ERROR = "PARSE_ERROR"
VALIDATION_ERROR = "VALIDATION_ERROR"


class ModelProvider(Protocol):
    """Provider-neutral model execution interface."""

    provider_name: str
    model_name: str

    def generate(
        self,
        prompt: str,
    ) -> Any:
        ...


@dataclass(frozen=True)
class ExecutionMetadata:
    provider_name: str
    model_name: str


def _require_non_empty_string(
    value: Any,
    name: str,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise ValueError(
            f"{name} must be a non-empty string."
        )

    return value.strip()


def _provider_metadata(
    provider: ModelProvider,
) -> ExecutionMetadata:
    provider_name = _require_non_empty_string(
        getattr(
            provider,
            "provider_name",
            None,
        ),
        "provider_name",
    )

    model_name = _require_non_empty_string(
        getattr(
            provider,
            "model_name",
            None,
        ),
        "model_name",
    )

    return ExecutionMetadata(
        provider_name=provider_name,
        model_name=model_name,
    )


def execute_governed_model(
    answer_context: dict,
    provider: ModelProvider,
) -> dict:
    """Execute a governed prompt through an untrusted model provider."""

    prompt_package = build_governed_prompt(
        answer_context
    )

    model_input = prompt_package[
        "model_input"
    ]

    metadata = _provider_metadata(
        provider
    )

    base_result = {
        "packet_id": model_input[
            "packet_id"
        ],
        "governance_decision": model_input[
            "governance_decision"
        ],
        "response_type": model_input[
            "response_type"
        ],
        "provider_name": (
            metadata.provider_name
        ),
        "model_name": (
            metadata.model_name
        ),
    }

    try:
        raw_output = provider.generate(
            prompt_package[
                "prompt"
            ]
        )
    except Exception as exc:
        return {
            **base_result,
            "execution_status": (
                EXECUTION_FAILED
            ),
            "fallback_used": True,
            "failure_type": (
                PROVIDER_ERROR
            ),
            "failure_reason": str(
                exc
            ),
            "validated_output": None,
            "raw_output": None,
        }

    if not isinstance(
        raw_output,
        dict,
    ):
        return {
            **base_result,
            "execution_status": (
                EXECUTION_REJECTED
            ),
            "fallback_used": True,
            "failure_type": (
                PARSE_ERROR
            ),
            "failure_reason": (
                "Provider output must be a structured mapping."
            ),
            "validated_output": None,
            "raw_output": raw_output,
        }

    try:
        validated_output = (
            validate_model_generation_output(
                model_input,
                raw_output,
            )
        )
    except Exception as exc:
        return {
            **base_result,
            "execution_status": (
                EXECUTION_REJECTED
            ),
            "fallback_used": True,
            "failure_type": (
                VALIDATION_ERROR
            ),
            "failure_reason": str(
                exc
            ),
            "validated_output": None,
            "raw_output": raw_output,
        }

    return {
        **base_result,
        "execution_status": (
            EXECUTION_ACCEPTED
        ),
        "fallback_used": False,
        "failure_type": None,
        "failure_reason": None,
        "validated_output": (
            validated_output
        ),
        "raw_output": raw_output,
    }