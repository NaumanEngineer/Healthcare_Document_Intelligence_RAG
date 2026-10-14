"""Tests for Week 24 deterministic generation fallback."""

from __future__ import annotations

from src.generation.generation_fallback import (
    FINAL_SOURCE_FALLBACK,
    FINAL_SOURCE_MODEL,
    resolve_generation_with_fallback,
)


def _accepted_execution() -> dict:
    return {
        "packet_id": "PKT-AUTO",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "provider_name": "deterministic_mock",
        "model_name": "week24-test-model",
        "execution_status": "ACCEPTED",
        "fallback_used": False,
        "failure_type": None,
        "failure_reason": None,
        "validated_output": {
            "packet_id": "PKT-AUTO",
            "governance_decision": "AUTO_ANSWER",
            "response_type": "ANSWER",
            "requires_human_review": False,
            "model_generation_status": "MODEL_GENERATED",
            "sections": {
                "management_summary": (
                    "Approved evidence supports coordinated escalation [E1]."
                ),
            },
            "citations_used": ["E1"],
            "model_safety_notes": [],
            "validation_status": "VALIDATED",
        },
        "raw_output": {},
    }


def _rejected_auto_execution() -> dict:
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


def _failed_review_execution() -> dict:
    return {
        "packet_id": "PKT-REVIEW",
        "governance_decision": "REVIEW_REQUIRED",
        "response_type": "REVIEW",
        "provider_name": "error_mock",
        "model_name": "week24-error-model",
        "execution_status": "FAILED",
        "fallback_used": True,
        "failure_type": "PROVIDER_ERROR",
        "failure_reason": "Provider unavailable.",
        "validated_output": None,
        "raw_output": None,
    }


def _failed_abstain_execution() -> dict:
    return {
        "packet_id": "PKT-ABSTAIN",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "provider_name": "free_text_mock",
        "model_name": "week24-free-text-model",
        "execution_status": "REJECTED",
        "fallback_used": True,
        "failure_type": "PARSE_ERROR",
        "failure_reason": (
            "Provider output must be a structured mapping."
        ),
        "validated_output": None,
        "raw_output": "free text",
    }


def _auto_deterministic_response() -> dict:
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
            "evidence_based_explanation": [
                {
                    "claim": (
                        "Escalation should be coordinated."
                    ),
                    "citation_ids": ["E1"],
                }
            ],
        },
        "citations_used": ["E1"],
    }


def _review_deterministic_response() -> dict:
    return {
        "packet_id": "PKT-REVIEW",
        "governance_decision": "REVIEW_REQUIRED",
        "response_type": "REVIEW",
        "requires_human_review": True,
        "generation_status": "REVIEW_SUMMARY",
        "sections": {
            "evidence_summary": (
                "Relevant evidence is available."
            ),
            "why_human_review_is_required": (
                "Human review is required before a final decision."
            ),
        },
        "citations_used": ["E1"],
    }


def _abstain_deterministic_response() -> dict:
    return {
        "packet_id": "PKT-ABSTAIN",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "requires_human_review": False,
        "generation_status": "ABSTAINED",
        "sections": {
            "unable_to_answer_safely": (
                "The approved evidence base is insufficient."
            ),
            "reason": (
                "Required evidence is missing."
            ),
            "missing_evidence": [
                "cybersecurity"
            ],
            "what_is_needed_to_continue": (
                "Provide approved cybersecurity guidance."
            ),
        },
        "citations_used": [],
    }


def test_accepted_model_output_is_used() -> None:
    result = resolve_generation_with_fallback(
        _accepted_execution(),
        _auto_deterministic_response(),
    )

    assert (
        result["final_response_source"]
        == FINAL_SOURCE_MODEL
    )

    assert result["fallback_used"] is False

    assert (
        result["final_response"][
            "model_generation_status"
        ]
        == "MODEL_GENERATED"
    )


def test_rejected_auto_output_uses_deterministic_fallback() -> None:
    result = resolve_generation_with_fallback(
        _rejected_auto_execution(),
        _auto_deterministic_response(),
    )

    assert (
        result["final_response_source"]
        == FINAL_SOURCE_FALLBACK
    )

    assert result["fallback_used"] is True

    assert (
        result["final_response"][
            "generation_status"
        ]
        == "GENERATED"
    )

    assert (
        result["fallback_reason"]
        == "Unknown citation ID: E99"
    )


def test_failed_review_execution_preserves_review_state() -> None:
    result = resolve_generation_with_fallback(
        _failed_review_execution(),
        _review_deterministic_response(),
    )

    assert (
        result["final_response_source"]
        == FINAL_SOURCE_FALLBACK
    )

    assert (
        result["governance_decision"]
        == "REVIEW_REQUIRED"
    )

    assert (
        result["response_type"]
        == "REVIEW"
    )

    assert (
        result["final_response"][
            "requires_human_review"
        ]
        is True
    )


def test_failed_abstain_execution_preserves_abstention() -> None:
    result = resolve_generation_with_fallback(
        _failed_abstain_execution(),
        _abstain_deterministic_response(),
    )

    assert (
        result["final_response_source"]
        == FINAL_SOURCE_FALLBACK
    )

    assert (
        result["governance_decision"]
        == "ABSTAIN"
    )

    assert (
        result["response_type"]
        == "ABSTENTION"
    )

    assert (
        result["final_response"][
            "citations_used"
        ]
        == []
    )


def test_model_provider_metadata_is_preserved() -> None:
    result = resolve_generation_with_fallback(
        _accepted_execution(),
        _auto_deterministic_response(),
    )

    assert (
        result["provider_name"]
        == "deterministic_mock"
    )

    assert (
        result["model_name"]
        == "week24-test-model"
    )


def test_fallback_provider_metadata_is_preserved() -> None:
    result = resolve_generation_with_fallback(
        _failed_review_execution(),
        _review_deterministic_response(),
    )

    assert (
        result["provider_name"]
        == "error_mock"
    )

    assert (
        result["model_name"]
        == "week24-error-model"
    )


def test_fallback_response_is_copied() -> None:
    fallback = _auto_deterministic_response()

    result = resolve_generation_with_fallback(
        _rejected_auto_execution(),
        fallback,
    )

    fallback[
        "sections"
    ][
        "management_summary"
    ] = "MUTATED"

    assert (
        result["final_response"][
            "sections"
        ][
            "management_summary"
        ]
        == "Deterministic management summary."
    )


def test_accepted_model_response_is_copied() -> None:
    execution = _accepted_execution()

    result = resolve_generation_with_fallback(
        execution,
        _auto_deterministic_response(),
    )

    execution[
        "validated_output"
    ][
        "sections"
    ][
        "management_summary"
    ] = "MUTATED"

    assert (
        result["final_response"][
            "sections"
        ][
            "management_summary"
        ]
        == "Approved evidence supports coordinated escalation [E1]."
    )