"""Tests for Week 24 controlled model execution."""

from __future__ import annotations

from src.generation.controlled_model_generation import (
    ABSTAIN,
    ANSWER,
    AUTO_ANSWER,
    MODEL_ABSTAINED,
    MODEL_GENERATED,
    MODEL_REVIEW_SUMMARY,
    REVIEW,
    REVIEW_REQUIRED,
)
from src.generation.mock_model_provider import (
    DeterministicMockProvider,
    ErrorMockProvider,
    FreeTextMockProvider,
)
from src.generation.model_execution import (
    EXECUTION_ACCEPTED,
    EXECUTION_FAILED,
    EXECUTION_REJECTED,
    PARSE_ERROR,
    PROVIDER_ERROR,
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


def _review_context() -> dict:
    context = _auto_context()

    context.update(
        {
            "packet_id": "PKT-REVIEW",
            "governance_decision": REVIEW_REQUIRED,
            "response_type": REVIEW,
            "generation_permitted": False,
            "requires_human_review": True,
            "allowed_sections": [
                "evidence_summary",
                "why_human_review_is_required",
                "review_focus",
                "evidence_gaps_or_uncertainty",
            ],
        }
    )

    return context


def _abstain_context() -> dict:
    return {
        "packet_id": "PKT-ABSTAIN",
        "question": "What should we do about cybersecurity?",
        "governance_decision": ABSTAIN,
        "response_type": "ABSTENTION",
        "generation_permitted": False,
        "requires_human_review": False,
        "allowed_sections": [
            "unable_to_answer_safely",
            "reason",
            "missing_information",
            "what_is_needed_to_continue",
        ],
        "safety_constraints": [
            "Do not provide substantive content.",
        ],
        "evidence_context": [],
        "citation_index": [],
        "uncertainty_context": {
            "initial_missing_topics": ["cybersecurity"],
            "final_missing_topics": ["cybersecurity"],
            "unsupported_claims": [],
        },
    }


def _valid_auto_output() -> dict:
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
        "citations_used": ["E1"],
        "model_safety_notes": [],
    }


def _valid_review_output() -> dict:
    return {
        "packet_id": "PKT-REVIEW",
        "governance_decision": REVIEW_REQUIRED,
        "response_type": REVIEW,
        "requires_human_review": True,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {
            "evidence_summary": (
                "Relevant approved evidence is available [E1]."
            ),
            "why_human_review_is_required": (
                "Human review remains mandatory."
            ),
        },
        "citations_used": ["E1"],
        "model_safety_notes": [],
    }


def _valid_abstain_output() -> dict:
    return {
        "packet_id": "PKT-ABSTAIN",
        "governance_decision": ABSTAIN,
        "response_type": "ABSTENTION",
        "requires_human_review": False,
        "model_generation_status": MODEL_ABSTAINED,
        "sections": {
            "unable_to_answer_safely": (
                "The approved evidence base is insufficient."
            ),
            "reason": (
                "No approved cybersecurity evidence is available."
            ),
            "missing_information": (
                "Approved cybersecurity guidance is not available "
                "in the evidence base."
            ),
            "what_is_needed_to_continue": (
                "Additional approved cybersecurity evidence is required."
            ),
        },
        "citations_used": [],
        "model_safety_notes": [],
    }


def test_valid_auto_execution_is_accepted() -> None:
    provider = DeterministicMockProvider(
        _valid_auto_output()
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_ACCEPTED
    assert result["fallback_used"] is False
    assert result["failure_type"] is None
    assert result["validated_output"] is not None
    assert result["validated_output"]["validation_status"] == "VALIDATED"


def test_valid_review_execution_is_accepted() -> None:
    provider = DeterministicMockProvider(
        _valid_review_output()
    )

    result = execute_governed_model(
        _review_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_ACCEPTED
    assert result["fallback_used"] is False
    assert result["governance_decision"] == REVIEW_REQUIRED


def test_valid_abstain_execution_is_accepted() -> None:
    provider = DeterministicMockProvider(
        _valid_abstain_output()
    )

    result = execute_governed_model(
        _abstain_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_ACCEPTED
    assert result["fallback_used"] is False
    assert result["validated_output"]["citations_used"] == []


def test_provider_error_uses_fallback() -> None:
    provider = ErrorMockProvider(
        "Provider unavailable."
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_FAILED
    assert result["fallback_used"] is True
    assert result["failure_type"] == PROVIDER_ERROR
    assert "Provider unavailable." in result["failure_reason"]
    assert result["validated_output"] is None


def test_free_text_output_is_rejected() -> None:
    provider = FreeTextMockProvider(
        "This is not structured."
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == PARSE_ERROR
    assert result["validated_output"] is None


def test_wrong_governance_is_rejected() -> None:
    output = _valid_review_output()
    output["governance_decision"] = AUTO_ANSWER

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _review_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR
    assert "governance mismatch" in result["failure_reason"]


def test_unknown_citation_is_rejected() -> None:
    output = _valid_auto_output()
    output["citations_used"] = ["E99"]

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
    assert "Unknown citation ID" in result["failure_reason"]


def test_packet_identity_mismatch_is_rejected() -> None:
    output = _valid_auto_output()
    output["packet_id"] = "WRONG"

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
    assert "packet identity mismatch" in result["failure_reason"]


def test_review_cannot_become_answer() -> None:
    output = _valid_review_output()
    output["response_type"] = ANSWER

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _review_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR
    assert "response type mismatch" in result["failure_reason"]


def test_abstain_cannot_use_citation() -> None:
    output = _valid_abstain_output()
    output["citations_used"] = ["E1"]

    provider = DeterministicMockProvider(
        output
    )

    result = execute_governed_model(
        _abstain_context(),
        provider,
    )

    assert result["execution_status"] == EXECUTION_REJECTED
    assert result["fallback_used"] is True
    assert result["failure_type"] == VALIDATION_ERROR


def test_provider_metadata_is_recorded() -> None:
    provider = DeterministicMockProvider(
        _valid_auto_output()
    )

    result = execute_governed_model(
        _auto_context(),
        provider,
    )

    assert result["provider_name"] == "deterministic_mock"
    assert result["model_name"] == "week24-test-model"