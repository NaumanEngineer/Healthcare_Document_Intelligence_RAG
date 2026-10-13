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
                    "Ambulance handover delays should be monitored "
                    "as part of the wider urgent and emergency care "
                    "pressure picture."
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
            "evidence_summary": [],
            "why_human_review_is_required": (
                "Human review is required before an "
                "authoritative answer is issued."
            ),
            "review_focus": {
                "precedence_decision": "SAFE_TO_COMBINE",
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
                    "Ambulance handover delays should be monitored "
                    "as part of wider operational pressure."
                ),
                "section": "evidence_summary",
                "citation_ids": ["E1"],
                "support_status": "SUPPORTED",
            }
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
                "The system cannot provide a substantive answer."
            ),
            "reason": (
                "The upstream governance decision is ABSTAIN."
            ),
            "missing_evidence": {},
            "what_is_needed_to_continue": (
                "Additional approved evidence is required."
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
                    "The system cannot provide "
                    "a substantive answer."
                ),
                "section": "unable_to_answer_safely",
                "citation_ids": [],
                "support_status": "NON_SUBSTANTIVE",
            }
        ],
    }


def test_review_status_remains_human_review_required():
    ux = build_review_abstention_ux(
        _review_response(),
        _review_context(),
        _review_linkage(),
    )

    assert (
        ux["manager_view"]["status"]
        == "HUMAN_REVIEW_REQUIRED"
    )


def test_review_next_action_does_not_authorise_automation():
    ux = build_review_abstention_ux(
        _review_response(),
        _review_context(),
        _review_linkage(),
    )

    next_action = (
        ux["manager_view"]["next_action"].lower()
    )

    assert "manager" in next_action
    assert "review" in next_action


def test_review_supported_evidence_stays_visible():
    ux = build_review_abstention_ux(
        _review_response(),
        _review_context(),
        _review_linkage(),
    )

    assert (
        ux["manager_view"]["evidence_summary"][0][
            "support_status"
        ]
        == "SUPPORTED"
    )


def test_abstain_status_remains_unable_to_answer_safely():
    ux = build_review_abstention_ux(
        _abstain_response(),
        _abstain_context(),
        _abstain_linkage(),
    )

    assert (
        ux["manager_view"]["status"]
        == "UNABLE_TO_ANSWER_SAFELY"
    )


def test_abstain_next_action_is_safe_escalation():
    ux = build_review_abstention_ux(
        _abstain_response(),
        _abstain_context(),
        _abstain_linkage(),
    )

    next_action = (
        ux["manager_view"]["safe_next_action"].lower()
    )

    assert (
        "approved evidence"
        in next_action
        or "operational owner"
        in next_action
    )


def test_abstain_does_not_gain_sources():
    ux = build_review_abstention_ux(
        _abstain_response(),
        _abstain_context(),
        _abstain_linkage(),
    )

    assert (
        "sources"
        not in ux["manager_view"]
    )


def test_abstain_with_context_evidence_fails_closed():
    context = _abstain_context()

    context["evidence_context"] = [
        {
            "evidence_text": "Hidden substantive content"
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


def test_abstain_with_supported_linkage_fails_closed():
    linkage = _abstain_linkage()

    linkage["claims"][0][
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