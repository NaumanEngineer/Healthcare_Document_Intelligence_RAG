"""Hardening tests for Week 24 controlled model execution."""

from __future__ import annotations

from src.generation.controlled_model_generation import (
    ANSWER,
    AUTO_ANSWER,
    MODEL_GENERATED,
)
from src.generation.mock_model_provider import (
    DeterministicMockProvider,
)
from src.generation.model_execution import (
    EXECUTION_REJECTED,
    VALIDATION_ERROR,
    execute_governed_model,
)


def _auto_context() -> dict:
    return {
        "packet_id": "PKT-AUTO",
        "question": "What should operational leadership do?",
        "governance_decision": AUTO_ANSWER,
        "response_type": ANSWER,
        "generation_permitted": True,
        "requires_human_review": False,
        "allowed_sections": [
            "management_summary",
            "evidence_based_explanation",
            "operational_implication",
            "caveats",
        ],
        "safety_constraints": [
            "Use approved evidence only.",
        ],
        "evidence_context": [
            {
                "evidence_id": "EV1",
                "document_id": "DOC001",
                "chunk_id": "DOC001-1",
                "title": "Operational Escalation Policy",
                "document_type": "policy",
                "source_file": "DOC001.pdf",
                "version": "1.0",
                "status": "Active",
                "page": 1,
                "evidence_text": "Escalation should be coordinated.",
                "evidence_role": "PRIMARY",
            }
        ],
        "citation_index": [
            {
                "citation_id": "E1",
                "document_id": "DOC001",
                "chunk_id": "DOC001-1",
                "status": "Active",
            }
        ],
        "uncertainty_context": {
            "initial_missing_topics": [],
            "final_missing_topics": [],
            "unsupported_claims": [],
        },
    }


def _valid_output() -> dict:
    return {
        "packet_id": "PKT-AUTO",
        "governance_decision": AUTO_ANSWER,
        "response_type": ANSWER,
        "requires_human_review": False,
        "model_generation_status": MODEL_GENERATED,
        "sections": {
            "management_summary": (
                "Approved evidence supports coordinated escalation [E1]."
            ),
        },
        "citations_used": [
            "E1"
        ],
        "model_safety_notes": [],
    }


def test_duplicate_citation_is_rejected() -> None:
    output = _valid_output()

    output["citations_used"] = [
        "E1",
        "E1",
    ]

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR
    assert "Duplicate citation ID" in result["failure_reason"]


def test_blank_citation_is_rejected() -> None:
    output = _valid_output()

    output["citations_used"] = [
        ""
    ]

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR


def test_prohibited_section_is_rejected() -> None:
    output = _valid_output()

    output["sections"][
        "final_decision"
    ] = "Implement immediately."

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR
    assert "prohibited sections" in result["failure_reason"]


def test_wrong_generation_status_is_rejected() -> None:
    output = _valid_output()

    output[
        "model_generation_status"
    ] = "MODEL_REVIEW_SUMMARY"

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR
    assert "generation status does not match governance" in result["failure_reason"]


def test_non_mapping_sections_are_rejected() -> None:
    output = _valid_output()

    output["sections"] = (
        "This is free-form text."
    )

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR
    assert "sections must be a mapping" in result["failure_reason"]


def test_missing_model_safety_notes_are_rejected() -> None:
    output = _valid_output()

    del output[
        "model_safety_notes"
    ]

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR


def test_missing_packet_id_is_rejected() -> None:
    output = _valid_output()

    del output[
        "packet_id"
    ]

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR


def test_raw_output_is_preserved_on_validation_failure() -> None:
    output = _valid_output()

    output["citations_used"] = [
        "E99"
    ]

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["raw_output"] is not None
    assert result["raw_output"]["citations_used"] == ["E99"]


def test_validated_output_is_none_on_rejection() -> None:
    output = _valid_output()

    output["packet_id"] = "WRONG"

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["validated_output"] is None


def test_fallback_does_not_change_authority() -> None:
    output = _valid_output()

    output["governance_decision"] = "REVIEW_REQUIRED"

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True

    assert (
        result["governance_decision"]
        == AUTO_ANSWER
    )

    assert (
        result["response_type"]
        == ANSWER
    )