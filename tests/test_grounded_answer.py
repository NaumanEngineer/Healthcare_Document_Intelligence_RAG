from __future__ import annotations

import pytest

from src.generation.grounded_answer import (
    build_grounded_response,
)


def _contract(
    decision: str,
) -> dict:
    if decision == "AUTO_ANSWER":
        return {
            "packet_id": "EVIDENCE_PACKET::TEST",
            "governance_decision": "AUTO_ANSWER",
            "response_type": "ANSWER",
            "response_sections": [
                "management_summary",
                "evidence_based_explanation",
                "operational_implication",
                "caveats",
                "sources",
            ],
            "may_generate_answer": True,
            "requires_human_review": False,
        }

    if decision == "REVIEW_REQUIRED":
        return {
            "packet_id": "EVIDENCE_PACKET::TEST",
            "governance_decision": "REVIEW_REQUIRED",
            "response_type": "REVIEW",
            "response_sections": [
                "evidence_summary",
                "why_human_review_is_required",
                "review_focus",
                "evidence_gaps_or_uncertainty",
                "sources",
            ],
            "may_generate_answer": False,
            "requires_human_review": True,
        }

    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "response_sections": [
            "unable_to_answer_safely",
            "reason",
            "missing_evidence",
            "what_is_needed_to_continue",
        ],
        "may_generate_answer": False,
        "requires_human_review": False,
    }


def _context(
    decision: str,
) -> dict:
    if decision == "AUTO_ANSWER":
        return {
            "context_version": "1.0",
            "packet_id": "EVIDENCE_PACKET::TEST",
            "question": (
                "Which guidance covers escalation "
                "when bed capacity is under pressure?"
            ),
            "governance_decision": "AUTO_ANSWER",
            "response_type": "ANSWER",
            "allowed_sections": [
                "management_summary",
                "evidence_based_explanation",
                "operational_implication",
                "caveats",
                "sources",
            ],
            "generation_permitted": True,
            "requires_human_review": False,
            "precedence_decision": "SAFE_TO_COMBINE",
            "evidence_context": [
                {
                    "evidence_id": (
                        "EVIDENCE::DOC-004-V1.0-P002-C001"
                    ),
                    "document_id": "DOC-004",
                    "chunk_id": (
                        "DOC-004-V1.0-P002-C001"
                    ),
                    "title": (
                        "Bed Capacity Management Procedure"
                    ),
                    "document_type": (
                        "Operational Procedure"
                    ),
                    "source_file": (
                        "DOC-004_"
                        "bed_capacity_management_"
                        "procedure.pdf"
                    ),
                    "version": "1.0",
                    "status": "Active",
                    "page": 2,
                    "evidence_text": (
                        "Bed capacity pressure should "
                        "be reviewed alongside site-flow "
                        "and escalation arrangements."
                    ),
                    "evidence_role": "supporting",
                }
            ],
            "citation_index": [
                {
                    "citation_id": "E1",
                    "evidence_id": (
                        "EVIDENCE::DOC-004-V1.0-P002-C001"
                    ),
                    "document_id": "DOC-004",
                    "chunk_id": (
                        "DOC-004-V1.0-P002-C001"
                    ),
                    "page": 2,
                    "source_file": (
                        "DOC-004_"
                        "bed_capacity_management_"
                        "procedure.pdf"
                    ),
                    "version": "1.0",
                    "status": "Active",
                }
            ],
            "uncertainty_context": {
                "initial_missing_topics": [],
                "final_missing_topics": [],
                "unsupported_claims": [],
            },
            "safety_constraints": [],
        }

    if decision == "REVIEW_REQUIRED":
        context = _context(
            "AUTO_ANSWER"
        )

        context[
            "governance_decision"
        ] = "REVIEW_REQUIRED"

        context[
            "response_type"
        ] = "REVIEW"

        context[
            "allowed_sections"
        ] = [
            "evidence_summary",
            "why_human_review_is_required",
            "review_focus",
            "evidence_gaps_or_uncertainty",
            "sources",
        ]

        context[
            "generation_permitted"
        ] = False

        context[
            "requires_human_review"
        ] = True

        return context

    return {
        "context_version": "1.0",
        "packet_id": "EVIDENCE_PACKET::TEST",
        "question": (
            "What is the approved operational procedure "
            "for managing hospital cyber-security incidents?"
        ),
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "allowed_sections": [
            "unable_to_answer_safely",
            "reason",
            "missing_evidence",
            "what_is_needed_to_continue",
        ],
        "generation_permitted": False,
        "requires_human_review": False,
        "precedence_decision": (
            "REVIEW_BEFORE_COMBINATION"
        ),
        "evidence_context": [],
        "citation_index": [],
        "uncertainty_context": {
            "initial_missing_topics": [
                "cyber-security incident procedure",
            ],
            "final_missing_topics": [
                "cyber-security incident procedure",
            ],
            "unsupported_claims": [],
        },
        "safety_constraints": [],
    }


def test_auto_answer_generates_grounded_response():
    response = build_grounded_response(
        _contract(
            "AUTO_ANSWER"
        ),
        _context(
            "AUTO_ANSWER"
        ),
    )

    assert (
        response["generation_status"]
        == "GENERATED"
    )

    assert (
        response["response_type"]
        == "ANSWER"
    )

    assert (
        response[
            "requires_human_review"
        ]
        is False
    )


def test_auto_answer_preserves_citation():
    response = build_grounded_response(
        _contract(
            "AUTO_ANSWER"
        ),
        _context(
            "AUTO_ANSWER"
        ),
    )

    assert (
        response["citations_used"]
        == ["E1"]
    )


def test_auto_answer_uses_evidence_text():
    response = build_grounded_response(
        _contract(
            "AUTO_ANSWER"
        ),
        _context(
            "AUTO_ANSWER"
        ),
    )

    evidence = response[
        "sections"
    ][
        "evidence_based_explanation"
    ][0]

    assert (
        "Bed capacity pressure"
        in evidence["evidence_text"]
    )


def test_review_required_creates_review_summary():
    response = build_grounded_response(
        _contract(
            "REVIEW_REQUIRED"
        ),
        _context(
            "REVIEW_REQUIRED"
        ),
    )

    assert (
        response["generation_status"]
        == "REVIEW_SUMMARY"
    )

    assert (
        response[
            "requires_human_review"
        ]
        is True
    )


def test_review_required_does_not_become_answer():
    response = build_grounded_response(
        _contract(
            "REVIEW_REQUIRED"
        ),
        _context(
            "REVIEW_REQUIRED"
        ),
    )

    assert (
        response["response_type"]
        == "REVIEW"
    )

    assert (
        "management_summary"
        not in response["sections"]
    )


def test_abstain_returns_abstention():
    response = build_grounded_response(
        _contract(
            "ABSTAIN"
        ),
        _context(
            "ABSTAIN"
        ),
    )

    assert (
        response["generation_status"]
        == "ABSTAINED"
    )

    assert (
        response["response_type"]
        == "ABSTENTION"
    )


def test_abstain_contains_no_citations():
    response = build_grounded_response(
        _contract(
            "ABSTAIN"
        ),
        _context(
            "ABSTAIN"
        ),
    )

    assert (
        response["citations_used"]
        == []
    )


def test_packet_id_mismatch_fails_closed():
    context = _context(
        "AUTO_ANSWER"
    )

    context[
        "packet_id"
    ] = "EVIDENCE_PACKET::OTHER"

    with pytest.raises(
        ValueError,
        match="packet IDs do not match",
    ):
        build_grounded_response(
            _contract(
                "AUTO_ANSWER"
            ),
            context,
        )


def test_governance_mismatch_fails_closed():
    with pytest.raises(
        ValueError,
        match="governance decisions do not match",
    ):
        build_grounded_response(
            _contract(
                "AUTO_ANSWER"
            ),
            _context(
                "REVIEW_REQUIRED"
            ),
        )


def test_response_type_mismatch_fails_closed():
    context = _context(
        "AUTO_ANSWER"
    )

    context[
        "response_type"
    ] = "REVIEW"

    with pytest.raises(
        ValueError,
        match="response types do not match",
    ):
        build_grounded_response(
            _contract(
                "AUTO_ANSWER"
            ),
            context,
        )


def test_generation_permission_mismatch_fails_closed():
    context = _context(
        "AUTO_ANSWER"
    )

    context[
        "generation_permitted"
    ] = False

    with pytest.raises(
        ValueError,
        match="generation permissions do not match",
    ):
        build_grounded_response(
            _contract(
                "AUTO_ANSWER"
            ),
            context,
        )


def test_human_review_mismatch_fails_closed():
    context = _context(
        "REVIEW_REQUIRED"
    )

    context[
        "requires_human_review"
    ] = False

    with pytest.raises(
        ValueError,
        match="human-review flags do not match",
    ):
        build_grounded_response(
            _contract(
                "REVIEW_REQUIRED"
            ),
            context,
        )


def test_auto_answer_without_evidence_fails_closed():
    context = _context(
        "AUTO_ANSWER"
    )

    context[
        "evidence_context"
    ] = []

    with pytest.raises(
        ValueError,
        match="AUTO_ANSWER requires approved evidence",
    ):
        build_grounded_response(
            _contract(
                "AUTO_ANSWER"
            ),
            context,
        )


def test_auto_answer_without_citations_fails_closed():
    context = _context(
        "AUTO_ANSWER"
    )

    context[
        "citation_index"
    ] = []

    with pytest.raises(
        ValueError,
        match="AUTO_ANSWER requires citations",
    ):
        build_grounded_response(
            _contract(
                "AUTO_ANSWER"
            ),
            context,
        )


def test_abstain_with_evidence_fails_closed():
    context = _context(
        "ABSTAIN"
    )

    context[
        "evidence_context"
    ] = [
        {
            "evidence_text": (
                "Hidden answer evidence"
            ),
        }
    ]

    with pytest.raises(
        ValueError,
        match=(
            "ABSTAIN must not contain substantive "
            "answer evidence"
        ),
    ):
        build_grounded_response(
            _contract(
                "ABSTAIN"
            ),
            context,
        )


def test_abstain_with_citation_fails_closed():
    context = _context(
        "ABSTAIN"
    )

    context[
        "citation_index"
    ] = [
        {
            "citation_id": "E1",
        }
    ]

    with pytest.raises(
        ValueError,
        match=(
            "ABSTAIN must not contain answer citations"
        ),
    ):
        build_grounded_response(
            _contract(
                "ABSTAIN"
            ),
            context,
        )