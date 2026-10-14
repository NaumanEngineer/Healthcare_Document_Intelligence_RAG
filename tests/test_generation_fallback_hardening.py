"""Hardening tests for Week 24 deterministic generation fallback."""

from __future__ import annotations

import pytest

from src.generation.generation_fallback import (
    FINAL_SOURCE_FALLBACK,
    resolve_generation_with_fallback,
)


def _rejected_execution() -> dict:
    return {
        "packet_id": "PKT-AUTO",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "provider_name": "deterministic_mock",
        "model_name": "week24-test-model",
        "execution_status": "REJECTED",
        "fallback_used": True,
        "failure_type": "VALIDATION_ERROR",
        "failure_reason": "Unknown citation ID: E99",
        "validated_output": None,
        "raw_output": {
            "citations_used": ["E99"],
        },
    }


def _fallback_response() -> dict:
    return {
        "packet_id": "PKT-AUTO",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "requires_human_review": False,
        "generation_status": "GENERATED",
        "sections": {
            "management_summary": (
                "Deterministic management summary."
            ),
        },
        "citations_used": ["E1"],
    }


def test_packet_identity_mismatch_fails_closed() -> None:
    fallback = _fallback_response()
    fallback["packet_id"] = "WRONG"

    with pytest.raises(
        ValueError,
        match="packet identity mismatch",
    ):
        resolve_generation_with_fallback(
            _rejected_execution(),
            fallback,
        )


def test_governance_mismatch_fails_closed() -> None:
    fallback = _fallback_response()
    fallback["governance_decision"] = "REVIEW_REQUIRED"

    with pytest.raises(
        ValueError,
        match="governance mismatch",
    ):
        resolve_generation_with_fallback(
            _rejected_execution(),
            fallback,
        )


def test_response_type_mismatch_fails_closed() -> None:
    fallback = _fallback_response()
    fallback["response_type"] = "REVIEW"

    with pytest.raises(
        ValueError,
        match="response type mismatch",
    ):
        resolve_generation_with_fallback(
            _rejected_execution(),
            fallback,
        )


def test_rejected_execution_must_require_fallback() -> None:
    execution = _rejected_execution()
    execution["fallback_used"] = False

    with pytest.raises(
        ValueError,
        match="must require fallback",
    ):
        resolve_generation_with_fallback(
            execution,
            _fallback_response(),
        )


def test_blank_failure_reason_fails_closed() -> None:
    execution = _rejected_execution()
    execution["failure_reason"] = ""

    with pytest.raises(
        ValueError,
        match="failure_reason must be a non-empty string",
    ):
        resolve_generation_with_fallback(
            execution,
            _fallback_response(),
        )


def test_blank_provider_name_fails_closed() -> None:
    execution = _rejected_execution()
    execution["provider_name"] = ""

    with pytest.raises(
        ValueError,
        match="provider_name must be a non-empty string",
    ):
        resolve_generation_with_fallback(
            execution,
            _fallback_response(),
        )


def test_blank_model_name_fails_closed() -> None:
    execution = _rejected_execution()
    execution["model_name"] = ""

    with pytest.raises(
        ValueError,
        match="model_name must be a non-empty string",
    ):
        resolve_generation_with_fallback(
            execution,
            _fallback_response(),
        )


def test_fallback_result_preserves_original_authority() -> None:
    result = resolve_generation_with_fallback(
        _rejected_execution(),
        _fallback_response(),
    )

    assert (
        result["final_response_source"]
        == FINAL_SOURCE_FALLBACK
    )

    assert (
        result["governance_decision"]
        == "AUTO_ANSWER"
    )

    assert (
        result["response_type"]
        == "ANSWER"
    )

    assert (
        result["final_response"][
            "requires_human_review"
        ]
        is False
    )


def test_fallback_does_not_use_rejected_raw_output() -> None:
    execution = _rejected_execution()

    result = resolve_generation_with_fallback(
        execution,
        _fallback_response(),
    )

    assert (
        result["final_response"]
        != execution["raw_output"]
    )

    assert (
        result["final_response"][
            "generation_status"
        ]
        == "GENERATED"
    )


def test_fallback_reason_is_recorded() -> None:
    result = resolve_generation_with_fallback(
        _rejected_execution(),
        _fallback_response(),
    )

    assert (
        result["fallback_reason"]
        == "Unknown citation ID: E99"
    )

    assert result["fallback_used"] is True