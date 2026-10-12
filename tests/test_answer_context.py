from __future__ import annotations

import pytest

from src.generation.answer_context import (
    build_answer_context,
)


def _evidence_item() -> dict:
    return {
        "evidence_id": "EVIDENCE::DOC-004-V1.0-P002-C001",
        "document_id": "DOC-004",
        "chunk_id": "DOC-004-V1.0-P002-C001",
        "title": "Bed Capacity Management Procedure",
        "document_type": "Operational Procedure",
        "source_file": "DOC-004_bed_capacity_management_procedure.pdf",
        "version": "1.0",
        "status": "Active",
        "page": 2,
        "evidence_text": (
            "Bed capacity pressure should be reviewed "
            "alongside site-flow and escalation arrangements."
        ),
        "evidence_role": "supporting",
    }


def _packet(
    decision: str,
    evidence: bool = True,
) -> dict:
    grouped_evidence = {
        "supporting": (
            [_evidence_item()]
            if evidence
            else []
        ),
        "relationship_evidence": [],
        "context": [],
    }

    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "question": (
            "Which guidance covers escalation "
            "when bed capacity is under pressure?"
        ),
        "governance": {
            "decision": decision,
        },
        "evidence": grouped_evidence,
        "missing_evidence": {
            "initial_missing_topics": [],
            "final_missing_topics": [],
            "unsupported_claims": [],
        },
        "precedence_assessment": {
            "decision": (
                "SAFE_TO_COMBINE"
                if evidence
                else "REVIEW_BEFORE_COMBINATION"
            ),
        },
    }


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


def test_auto_answer_context_preserves_evidence():
    context = build_answer_context(
        _packet(
            "AUTO_ANSWER"
        ),
        _contract(
            "AUTO_ANSWER"
        ),
    )

    assert (
        context["governance_decision"]
        == "AUTO_ANSWER"
    )

    assert (
        context["generation_permitted"]
        is True
    )

    assert (
        len(
            context["evidence_context"]
        )
        == 1
    )

    assert (
        context[
            "evidence_context"
        ][0][
            "document_id"
        ]
        == "DOC-004"
    )


def test_auto_answer_builds_stable_citation_index():
    context = build_answer_context(
        _packet(
            "AUTO_ANSWER"
        ),
        _contract(
            "AUTO_ANSWER"
        ),
    )

    assert (
        context["citation_index"]
        == [
            {
                "citation_id": "E1",
                "evidence_id": (
                    "EVIDENCE::DOC-004-"
                    "V1.0-P002-C001"
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
        ]
    )


def test_review_required_keeps_evidence_but_blocks_generation():
    context = build_answer_context(
        _packet(
            "REVIEW_REQUIRED"
        ),
        _contract(
            "REVIEW_REQUIRED"
        ),
    )

    assert (
        context["requires_human_review"]
        is True
    )

    assert (
        context["generation_permitted"]
        is False
    )

    assert (
        len(
            context["evidence_context"]
        )
        == 1
    )


def test_abstain_context_contains_no_substantive_evidence():
    context = build_answer_context(
        _packet(
            "ABSTAIN",
            evidence=False,
        ),
        _contract(
            "ABSTAIN"
        ),
    )

    assert (
        context["generation_permitted"]
        is False
    )

    assert (
        context["evidence_context"]
        == []
    )

    assert (
        context["citation_index"]
        == []
    )


def test_packet_id_mismatch_fails_closed():
    contract = _contract(
        "AUTO_ANSWER"
    )

    contract[
        "packet_id"
    ] = "EVIDENCE_PACKET::OTHER"

    with pytest.raises(
        ValueError,
        match="packet IDs do not match",
    ):
        build_answer_context(
            _packet(
                "AUTO_ANSWER"
            ),
            contract,
        )


def test_governance_mismatch_fails_closed():
    with pytest.raises(
        ValueError,
        match="governance decisions do not match",
    ):
        build_answer_context(
            _packet(
                "AUTO_ANSWER"
            ),
            _contract(
                "REVIEW_REQUIRED"
            ),
        )


def test_non_abstain_without_evidence_fails_closed():
    with pytest.raises(
        ValueError,
        match=(
            "Non-ABSTAIN Answer Context "
            "requires approved evidence"
        ),
    ):
        build_answer_context(
            _packet(
                "AUTO_ANSWER",
                evidence=False,
            ),
            _contract(
                "AUTO_ANSWER"
            ),
        )


def test_missing_required_evidence_field_fails_closed():
    packet = _packet(
        "AUTO_ANSWER"
    )

    del packet[
        "evidence"
    ][
        "supporting"
    ][0][
        "evidence_text"
    ]

    with pytest.raises(
        ValueError,
        match="missing required Answer Context fields",
    ):
        build_answer_context(
            packet,
            _contract(
                "AUTO_ANSWER"
            ),
        )


def test_missing_question_fails_closed():
    packet = _packet(
        "AUTO_ANSWER"
    )

    del packet[
        "question"
    ]

    with pytest.raises(
        TypeError,
        match="evidence_packet.question",
    ):
        build_answer_context(
            packet,
            _contract(
                "AUTO_ANSWER"
            ),
        )


def test_generation_permission_must_be_boolean():
    contract = _contract(
        "AUTO_ANSWER"
    )

    contract[
        "may_generate_answer"
    ] = "yes"

    with pytest.raises(
        TypeError,
        match="may_generate_answer",
    ):
        build_answer_context(
            _packet(
                "AUTO_ANSWER"
            ),
            contract,
        )


def test_human_review_flag_must_be_boolean():
    contract = _contract(
        "REVIEW_REQUIRED"
    )

    contract[
        "requires_human_review"
    ] = "yes"

    with pytest.raises(
        TypeError,
        match="requires_human_review",
    ):
        build_answer_context(
            _packet(
                "REVIEW_REQUIRED"
            ),
            contract,
        )


def test_context_excludes_retrieval_noise():
    packet = _packet(
        "AUTO_ANSWER"
    )

    packet[
        "evidence"
    ][
        "supporting"
    ][0][
        "similarity_score"
    ] = 0.987

    packet[
        "evidence"
    ][
        "supporting"
    ][0][
        "keyword_score"
    ] = 99.0

    context = build_answer_context(
        packet,
        _contract(
            "AUTO_ANSWER"
        ),
    )

    evidence = (
        context[
            "evidence_context"
        ][0]
    )

    assert (
        "similarity_score"
        not in evidence
    )

    assert (
        "keyword_score"
        not in evidence
    )