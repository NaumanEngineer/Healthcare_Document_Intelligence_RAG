"""Tests for Week 24 controlled model generation."""

from __future__ import annotations

import pytest

from src.generation.controlled_model_generation import (
    ABSTAIN,
    ANSWER,
    AUTO_ANSWER,
    MODEL_ABSTAINED,
    MODEL_GENERATED,
    MODEL_REVIEW_SUMMARY,
    REVIEW,
    REVIEW_REQUIRED,
    build_model_generation_input,
    validate_model_generation_output,
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
            "Do not invent citations.",
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
            "Do not provide a substantive answer.",
        ],
        "evidence_context": [],
        "citation_index": [],
        "uncertainty_context": {
            "initial_missing_topics": ["cybersecurity"],
            "final_missing_topics": ["cybersecurity"],
            "unsupported_claims": [],
        },
    }


def test_build_auto_model_input() -> None:
    result = build_model_generation_input(
        _auto_context()
    )

    assert result["packet_id"] == "PKT-AUTO"
    assert result["governance_decision"] == AUTO_ANSWER
    assert result["response_type"] == ANSWER
    assert result["generation_permitted"] is True
    assert result["requires_human_review"] is False
    assert len(result["evidence_context"]) == 1
    assert len(result["citation_index"]) == 1


def test_build_review_model_input() -> None:
    result = build_model_generation_input(
        _review_context()
    )

    assert result["governance_decision"] == REVIEW_REQUIRED
    assert result["response_type"] == REVIEW
    assert result["generation_permitted"] is False
    assert result["requires_human_review"] is True


def test_build_abstain_model_input() -> None:
    result = build_model_generation_input(
        _abstain_context()
    )

    assert result["governance_decision"] == ABSTAIN
    assert result["generation_permitted"] is False
    assert result["evidence_context"] == []
    assert result["citation_index"] == []


def test_auto_output_validates() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = {
        "packet_id": "PKT-AUTO",
        "governance_decision": AUTO_ANSWER,
        "response_type": ANSWER,
        "requires_human_review": False,
        "model_generation_status": MODEL_GENERATED,
        "sections": {
            "management_summary": "Escalation should be coordinated [E1].",
            "evidence_based_explanation": (
                "The approved policy supports coordinated escalation [E1]."
            ),
            "operational_implication": (
                "Leadership should use the approved escalation route [E1]."
            ),
            "caveats": "This answer is based only on the supplied evidence.",
        },
        "citations_used": ["E1"],
        "model_safety_notes": [],
    }

    result = validate_model_generation_output(
        model_input,
        output,
    )

    assert result["validation_status"] == "VALIDATED"
    assert result["model_generation_status"] == MODEL_GENERATED
    assert result["citations_used"] == ["E1"]


def test_review_output_validates() -> None:
    model_input = build_model_generation_input(
        _review_context()
    )

    output = {
        "packet_id": "PKT-REVIEW",
        "governance_decision": REVIEW_REQUIRED,
        "response_type": REVIEW,
        "requires_human_review": True,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {
            "evidence_summary": "Relevant evidence is available [E1].",
            "why_human_review_is_required": (
                "The governance state requires human review."
            ),
            "review_focus": "Review the approved policy evidence.",
            "evidence_gaps_or_uncertainty": "No additional gap recorded.",
        },
        "citations_used": ["E1"],
        "model_safety_notes": [],
    }

    result = validate_model_generation_output(
        model_input,
        output,
    )

    assert result["validation_status"] == "VALIDATED"
    assert result["requires_human_review"] is True
    assert result["model_generation_status"] == MODEL_REVIEW_SUMMARY


def test_abstain_output_validates() -> None:
    model_input = build_model_generation_input(
        _abstain_context()
    )

    output = {
        "packet_id": "PKT-ABSTAIN",
        "governance_decision": ABSTAIN,
        "response_type": "ABSTENTION",
        "requires_human_review": False,
        "model_generation_status": MODEL_ABSTAINED,
        "sections": {
            "unable_to_answer_safely": (
                "The approved evidence base is insufficient."
            ),
            "reason": "No approved cybersecurity evidence is available.",
            "missing_information": "Cybersecurity evidence is missing.",
            "what_is_needed_to_continue": (
                "Provide approved cybersecurity guidance."
            ),
        },
        "citations_used": [],
        "model_safety_notes": [],
    }

    result = validate_model_generation_output(
        model_input,
        output,
    )

    assert result["validation_status"] == "VALIDATED"
    assert result["citations_used"] == []


def test_unknown_citation_fails_closed() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = {
        "packet_id": "PKT-AUTO",
        "governance_decision": AUTO_ANSWER,
        "response_type": ANSWER,
        "requires_human_review": False,
        "model_generation_status": MODEL_GENERATED,
        "sections": {
            "management_summary": "Example.",
        },
        "citations_used": ["E99"],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="Unknown citation ID",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_packet_identity_mismatch_fails_closed() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = {
        "packet_id": "WRONG",
        "governance_decision": AUTO_ANSWER,
        "response_type": ANSWER,
        "requires_human_review": False,
        "model_generation_status": MODEL_GENERATED,
        "sections": {},
        "citations_used": [],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="packet identity mismatch",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_governance_mismatch_fails_closed() -> None:
    model_input = build_model_generation_input(
        _review_context()
    )

    output = {
        "packet_id": "PKT-REVIEW",
        "governance_decision": AUTO_ANSWER,
        "response_type": REVIEW,
        "requires_human_review": True,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {},
        "citations_used": [],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="governance mismatch",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_review_cannot_become_answer() -> None:
    model_input = build_model_generation_input(
        _review_context()
    )

    output = {
        "packet_id": "PKT-REVIEW",
        "governance_decision": REVIEW_REQUIRED,
        "response_type": ANSWER,
        "requires_human_review": True,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {},
        "citations_used": [],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="response type mismatch",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_review_must_keep_human_review() -> None:
    model_input = build_model_generation_input(
        _review_context()
    )

    output = {
        "packet_id": "PKT-REVIEW",
        "governance_decision": REVIEW_REQUIRED,
        "response_type": REVIEW,
        "requires_human_review": False,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {},
        "citations_used": [],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="human-review state mismatch",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_abstain_input_rejects_evidence_leak() -> None:
    context = _abstain_context()

    context["evidence_context"] = [
        {
            "evidence_id": "LEAK",
        }
    ]

    with pytest.raises(
        ValueError,
        match="must not contain substantive evidence",
    ):
        build_model_generation_input(
            context
        )


def test_abstain_input_rejects_citation_leak() -> None:
    context = _abstain_context()

    context["citation_index"] = [
        {
            "citation_id": "E1",
        }
    ]

    with pytest.raises(
        ValueError,
        match="must not contain citations",
    ):
        build_model_generation_input(
            context
        )


def test_prohibited_section_fails_closed() -> None:
    model_input = build_model_generation_input(
        _review_context()
    )

    output = {
        "packet_id": "PKT-REVIEW",
        "governance_decision": REVIEW_REQUIRED,
        "response_type": REVIEW,
        "requires_human_review": True,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {
            "approved_action": "Implement immediately.",
        },
        "citations_used": [],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="prohibited sections",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_wrong_generation_status_fails_closed() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = {
        "packet_id": "PKT-AUTO",
        "governance_decision": AUTO_ANSWER,
        "response_type": ANSWER,
        "requires_human_review": False,
        "model_generation_status": MODEL_REVIEW_SUMMARY,
        "sections": {},
        "citations_used": [],
        "model_safety_notes": [],
    }

    with pytest.raises(
        ValueError,
        match="generation status does not match governance",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )