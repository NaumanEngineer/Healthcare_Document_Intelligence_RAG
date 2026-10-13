from __future__ import annotations

import pytest

from src.generation.review_abstention_ux import (
    build_review_abstention_ux,
)


def _review_context() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "REVIEW_REQUIRED",
        "response_type": "REVIEW",
        "evidence_context": [
            {
                "evidence_id": "EVIDENCE::DOC-008-V1.0-P001-C001",
                "document_id": "DOC-008",
                "chunk_id": "DOC-008-V1.0-P001-C001",
                "title": "Ambulance Handover Escalation Guidance",
                "document_type": "Operational Guidance",
                "source_file": (
                    "DOC-008_ambulance_handover_"
                    "escalation_guidance.pdf"
                ),
                "version": "1.0",
                "status": "Active",
                "page": 1,
                "evidence_text": (
                    "Ambulance handover delays should be "
                    "monitored as part of the wider urgent "
                    "and emergency care pressure picture."
                ),
                "evidence_role": "supporting",
            }
        ],
        "citation_index": [
            {
                "citation_id": "E1",
                "evidence_id": "EVIDENCE::DOC-008-V1.0-P001-C001",
                "document_id": "DOC-008",
                "chunk_id": "DOC-008-V1.0-P001-C001",
                "page": 1,
                "source_file": (
                    "DOC-008_ambulance_handover_"
                    "escalation_guidance.pdf"
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
    }


def _review_response() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "REVIEW_REQUIRED",
        "response_type": "REVIEW",
        "requires_human_review": True,
        "sections": {
            "evidence_summary": [
                {
                    "citation_id": "E1",
                    "document_id": "DOC-008",
                    "evidence_text": (
                        "Ambulance handover delays should be "
                        "monitored as part of wider pressure."
                    ),
                }
            ],
            "why_human_review_is_required": (
                "The upstream governance decision requires "
                "human review before an authoritative answer "
                "or operational recommendation is issued."
            ),
            "review_focus": {
                "precedence_decision": "SAFE_TO_COMBINE",
                "question": (
                    "How should severe weather pressure and "
                    "ambulance handover disruption be considered?"
                ),
            },
            "evidence_gaps_or_uncertainty": {},
            "sources": [],
        },
    }


def _review_linkage() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "REVIEW_REQUIRED",
        "response_type": "REVIEW",
        "claims": [
            {
                "claim_id": "C1",
                "claim_text": (
                    "Ambulance handover delays should be "
                    "monitored as part of wider pressure."
                ),
                "section": "evidence_summary",
                "citation_ids": ["E1"],
                "support_status": "SUPPORTED",
            },
            {
                "claim_id": "C2",
                "claim_text": (
                    "Human review is required."
                ),
                "section": "why_human_review_is_required",
                "citation_ids": [],
                "support_status": "NON_SUBSTANTIVE",
            },
        ],
    }


def _abstain_context() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "evidence_context": [],
        "citation_index": [],
        "uncertainty_context": {
            "initial_missing_topics": [
                "cybersecurity",
            ],
            "final_missing_topics": [
                "cybersecurity",
            ],
            "unsupported_claims": [],
        },
    }


def _abstain_response() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "requires_human_review": False,
        "sections": {
            "unable_to_answer_safely": (
                "The system cannot provide a substantive "
                "answer from the approved evidence."
            ),
            "reason": (
                "The upstream governance decision is ABSTAIN."
            ),
            "missing_evidence": {
                "final_missing_topics": [
                    "cybersecurity",
                ],
            },
            "what_is_needed_to_continue": (
                "Additional approved evidence or scope "
                "clarification is required before a "
                "substantive answer can be generated."
            ),
        },
    }


def _abstain_linkage() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "claims": [
            {
                "claim_id": "C1",
                "claim_text": (
                    "The system cannot provide a "
                    "substantive answer."
                ),
                "section": "unable_to_answer_safely",
                "citation_ids": [],
                "support_status": "NON_SUBSTANTIVE",
            }
        ],
    }


def test_review_required_builds_manager_view():
    ux = build_review_abstention_ux(
        _review_response(),
        _review_context(),
        _review_linkage(),
    )

    assert (
        ux["manager_view"]["status"]
        == "HUMAN_REVIEW_REQUIRED"
    )


def test_review_required_keeps_supported_evidence_visible():
    ux = build_review_abstention_ux(
        _review_response(),
        _review_context(),
        _review_linkage(),
    )

    assert (
        len(
            ux["manager_view"]["evidence_summary"]
        )
        == 1
    )

    assert (
        ux["manager_view"]["evidence_summary"][0][
            "support_status"
        ]
        == "SUPPORTED"
    )


def test_review_required_exposes_sources():
    ux = build_review_abstention_ux(
        _review_response(),
        _review_context(),
        _review_linkage(),
    )

    assert (
        ux["manager_view"]["sources"][0][
            "citation_id"
        ]
        == "E1"
    )


def test_review_required_requires_human_review():
    response = _review_response()

    response[
        "requires_human_review"
    ] = False

    with pytest.raises(
        ValueError,
        match="must require human review",
    ):
        build_review_abstention_ux(
            response,
            _review_context(),
            _review_linkage(),
        )


def test_abstain_builds_safe_manager_view():
    ux = build_review_abstention_ux(
        _abstain_response(),
        _abstain_context(),
        _abstain_linkage(),
    )

    assert (
        ux["manager_view"]["status"]
        == "UNABLE_TO_ANSWER_SAFELY"
    )


def test_abstain_exposes_missing_information():
    ux = build_review_abstention_ux(
        _abstain_response(),
        _abstain_context(),
        _abstain_linkage(),
    )

    assert (
        "cybersecurity"
        in ux[
            "manager_view"
        ][
            "missing_information"
        ][
            "final_missing_topics"
        ]
    )


def test_abstain_does_not_expose_sources():
    ux = build_review_abstention_ux(
        _abstain_response(),
        _abstain_context(),
        _abstain_linkage(),
    )

    assert (
        "sources"
        not in ux["manager_view"]
    )


def test_abstain_with_evidence_fails_closed():
    context = _abstain_context()

    context[
        "evidence_context"
    ] = [
        {
            "evidence_text": "Hidden answer evidence"
        }
    ]

    with pytest.raises(
        ValueError,
        match="must not expose substantive answer evidence",
    ):
        build_review_abstention_ux(
            _abstain_response(),
            context,
            _abstain_linkage(),
        )


def test_abstain_with_supported_claim_fails_closed():
    linkage = _abstain_linkage()

    linkage[
        "claims"
    ][0][
        "support_status"
    ] = "SUPPORTED"

    with pytest.raises(
        ValueError,
        match="must not contain supported substantive claims",
    ):
        build_review_abstention_ux(
            _abstain_response(),
            _abstain_context(),
            linkage,
        )


def test_packet_mismatch_fails_closed():
    response = _review_response()

    response[
        "packet_id"
    ] = "EVIDENCE_PACKET::OTHER"

    with pytest.raises(
        ValueError,
        match="Packet IDs do not match",
    ):
        build_review_abstention_ux(
            response,
            _review_context(),
            _review_linkage(),
        )


def test_governance_mismatch_fails_closed():
    linkage = _review_linkage()

    linkage[
        "governance_decision"
    ] = "ABSTAIN"

    with pytest.raises(
        ValueError,
        match="Governance decisions do not match",
    ):
        build_review_abstention_ux(
            _review_response(),
            _review_context(),
            linkage,
        )


def test_response_type_mismatch_fails_closed():
    context = _review_context()

    context[
        "response_type"
    ] = "ABSTENTION"

    with pytest.raises(
        ValueError,
        match="Response types do not match",
    ):
        build_review_abstention_ux(
            _review_response(),
            context,
            _review_linkage(),
        )


def test_auto_answer_is_not_supported_by_this_ux():
    response = _review_response()
    context = _review_context()
    linkage = _review_linkage()

    response[
        "governance_decision"
    ] = "AUTO_ANSWER"

    context[
        "governance_decision"
    ] = "AUTO_ANSWER"

    linkage[
        "governance_decision"
    ] = "AUTO_ANSWER"

    with pytest.raises(
        ValueError,
        match="only supports REVIEW_REQUIRED or ABSTAIN",
    ):
        build_review_abstention_ux(
            response,
            context,
            linkage,
        )