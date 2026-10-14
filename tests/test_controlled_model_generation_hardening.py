"""Hardening tests for Week 24 controlled model generation."""

from __future__ import annotations

import pytest

from src.generation.controlled_model_generation import (
    ABSTAIN,
    ANSWER,
    AUTO_ANSWER,
    MODEL_ABSTAINED,
    MODEL_GENERATED,
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
            "initial_missing_topics": [
                "cybersecurity"
            ],
            "final_missing_topics": [
                "cybersecurity"
            ],
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
        "citations_used": [
            "E1"
        ],
        "model_safety_notes": [],
    }


def test_unsupported_governance_fails_closed() -> None:
    context = _auto_context()
    context["governance_decision"] = "UNKNOWN"

    with pytest.raises(
        ValueError,
        match="Unsupported governance decision",
    ):
        build_model_generation_input(
            context
        )


def test_auto_answer_cannot_disable_generation_permission() -> None:
    context = _auto_context()
    context["generation_permitted"] = False

    with pytest.raises(
        ValueError,
        match="AUTO_ANSWER requires generation_permitted=true",
    ):
        build_model_generation_input(
            context
        )


def test_review_cannot_enable_authoritative_generation() -> None:
    context = _review_context()
    context["generation_permitted"] = True

    with pytest.raises(
        ValueError,
        match="must not permit authoritative generation",
    ):
        build_model_generation_input(
            context
        )


def test_abstain_cannot_be_changed_to_review_state() -> None:
    context = _abstain_context()
    context["requires_human_review"] = True

    with pytest.raises(
        ValueError,
        match="should not convert into a review state",
    ):
        build_model_generation_input(
            context
        )


def test_blank_output_citation_fails_closed() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = _valid_auto_output()
    output["citations_used"] = [""]

    with pytest.raises(
        ValueError,
        match="citation used must be a non-empty string",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_duplicate_output_citation_fails_closed() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = _valid_auto_output()
    output["citations_used"] = [
        "E1",
        "E1",
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate citation ID",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_duplicate_input_citation_ids_fail_closed() -> None:
    context = _auto_context()

    context["citation_index"].append(
        {
            "citation_id": "E1",
            "document_id": "DOC999",
            "chunk_id": "DOC999-1",
            "status": "Active",
        }
    )

    model_input = build_model_generation_input(
        context
    )

    output = _valid_auto_output()

    with pytest.raises(
        ValueError,
        match="Duplicate citation ID in model input",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_answer_cannot_add_unapproved_section() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = _valid_auto_output()

    output["sections"][
        "final_decision"
    ] = "Implement immediately."

    with pytest.raises(
        ValueError,
        match="prohibited sections",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_sections_must_be_structured_mapping() -> None:
    model_input = build_model_generation_input(
        _auto_context()
    )

    output = _valid_auto_output()
    output["sections"] = "free-form answer"

    with pytest.raises(
        ValueError,
        match="sections must be a mapping",
    ):
        validate_model_generation_output(
            model_input,
            output,
        )


def test_model_input_is_isolated_from_source_context_mutation() -> None:
    context = _auto_context()

    model_input = build_model_generation_input(
        context
    )

    context[
        "evidence_context"
    ][0][
        "evidence_text"
    ] = "MUTATED"

    context[
        "citation_index"
    ][0][
        "citation_id"
    ] = "CHANGED"

    assert (
        model_input[
            "evidence_context"
        ][0][
            "evidence_text"
        ]
        == "Escalation should be coordinated."
    )

    assert (
        model_input[
            "citation_index"
        ][0][
            "citation_id"
        ]
        == "E1"
    )


def test_abstain_wrong_generation_status_fails_closed() -> None:
    model_input = build_model_generation_input(
        _abstain_context()
    )

    output = {
        "packet_id": "PKT-ABSTAIN",
        "governance_decision": ABSTAIN,
        "response_type": "ABSTENTION",
        "requires_human_review": False,
        "model_generation_status": MODEL_GENERATED,
        "sections": {
            "unable_to_answer_safely": (
                "The evidence base is insufficient."
            ),
        },
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