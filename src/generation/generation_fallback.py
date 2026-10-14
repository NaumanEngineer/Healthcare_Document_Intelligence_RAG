"""Week 24 Day 4 — deterministic fallback integration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.generation.model_execution import (
    EXECUTION_ACCEPTED,
)


FINAL_SOURCE_MODEL = "MODEL"
FINAL_SOURCE_FALLBACK = "DETERMINISTIC_FALLBACK"


def _require_mapping(
    value: Any,
    name: str,
) -> dict:
    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"{name} must be a mapping."
        )

    return value


def _require_bool(
    value: Any,
    name: str,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise ValueError(
            f"{name} must be a boolean."
        )

    return value


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


def _validate_identity(
    execution_result: dict,
    deterministic_response: dict,
) -> None:
    packet_id = _require_non_empty_string(
        execution_result.get(
            "packet_id"
        ),
        "execution packet_id",
    )

    fallback_packet_id = _require_non_empty_string(
        deterministic_response.get(
            "packet_id"
        ),
        "deterministic packet_id",
    )

    if packet_id != fallback_packet_id:
        raise ValueError(
            "Execution and deterministic response packet identity mismatch."
        )

    governance_decision = _require_non_empty_string(
        execution_result.get(
            "governance_decision"
        ),
        "execution governance_decision",
    )

    fallback_governance = _require_non_empty_string(
        deterministic_response.get(
            "governance_decision"
        ),
        "deterministic governance_decision",
    )

    if governance_decision != fallback_governance:
        raise ValueError(
            "Execution and deterministic response governance mismatch."
        )

    response_type = _require_non_empty_string(
        execution_result.get(
            "response_type"
        ),
        "execution response_type",
    )

    fallback_response_type = _require_non_empty_string(
        deterministic_response.get(
            "response_type"
        ),
        "deterministic response_type",
    )

    if response_type != fallback_response_type:
        raise ValueError(
            "Execution and deterministic response type mismatch."
        )


def resolve_generation_with_fallback(
    execution_result: dict,
    deterministic_response: dict,
) -> dict:
    """Resolve final response from model execution or deterministic fallback."""

    execution = _require_mapping(
        execution_result,
        "execution_result",
    )

    fallback = _require_mapping(
        deterministic_response,
        "deterministic_response",
    )

    _validate_identity(
        execution,
        fallback,
    )

    execution_status = _require_non_empty_string(
        execution.get(
            "execution_status"
        ),
        "execution_status",
    )

    provider_name = _require_non_empty_string(
        execution.get(
            "provider_name"
        ),
        "provider_name",
    )

    model_name = _require_non_empty_string(
        execution.get(
            "model_name"
        ),
        "model_name",
    )

    fallback_used = _require_bool(
        execution.get(
            "fallback_used"
        ),
        "fallback_used",
    )

    if execution_status == EXECUTION_ACCEPTED:
        if fallback_used is not False:
            raise ValueError(
                "Accepted model execution must not already require fallback."
            )

        validated_output = _require_mapping(
            execution.get(
                "validated_output"
            ),
            "validated_output",
        )

        return {
            "packet_id": execution[
                "packet_id"
            ],
            "governance_decision": execution[
                "governance_decision"
            ],
            "response_type": execution[
                "response_type"
            ],
            "final_response_source": (
                FINAL_SOURCE_MODEL
            ),
            "fallback_used": False,
            "fallback_reason": None,
            "provider_name": provider_name,
            "model_name": model_name,
            "model_execution_status": (
                execution_status
            ),
            "final_response": deepcopy(
                validated_output
            ),
        }

    if fallback_used is not True:
        raise ValueError(
            "Rejected or failed model execution must require fallback."
        )

    failure_reason = _require_non_empty_string(
        execution.get(
            "failure_reason"
        ),
        "failure_reason",
    )

    return {
        "packet_id": execution[
            "packet_id"
        ],
        "governance_decision": execution[
            "governance_decision"
        ],
        "response_type": execution[
            "response_type"
        ],
        "final_response_source": (
            FINAL_SOURCE_FALLBACK
        ),
        "fallback_used": True,
        "fallback_reason": (
            failure_reason
        ),
        "provider_name": provider_name,
        "model_name": model_name,
        "model_execution_status": (
            execution_status
        ),
        "final_response": deepcopy(
            fallback
        ),
    }