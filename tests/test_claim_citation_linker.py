from __future__ import annotations

import pytest

from src.generation.claim_citation_linker import (
    build_claim_citation_links,
)


def _answer_context(
    decision: str,
) -> dict:
    base = {
        "context_version": "1.0",
        "packet_id": "EVIDENCE_PACKET::TEST",
        "question": "Test question",
        "governance_decision": decision,
        "response_type": (
            "ANSWER"
            if decision == "AUTO_ANSWER"
            else (
                "REVIEW"
                if decision == "REVIEW_REQUIRED"
                else "ABSTENTION"
            )
        ),
        "citation_index": [],
    }

    if decision in (
        "AUTO_ANSWER",
        "REVIEW_REQUIRED",
    ):
        base[
            "citation_index"
        ] = [
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
        ]

    return base


def _grounded_response(
    decision: str,
) -> dict:
    if decision == "AUTO_ANSWER":
        return {
            "packet_id": "EVIDENCE_PACKET::TEST",
            "governance_decision": "AUTO_ANSWER",
            "response_type": "ANSWER",
            "citations_used": [
                "E1"
            ],
            "sections": {
                "management_summary": (
                    "Approved evidence is available "
                    "to answer the management question."
                ),
                "evidence_based_explanation": [
                    {
                        "citation_id": "E1",
                        "document_id": "DOC-004",
                        "evidence_text": (
                            "Bed capacity pressure should "
                            "be reviewed alongside site-flow "
                            "and escalation arrangements."
                        ),
                    }
                ],
                "operational_implication": (
                    "Use the approved evidence above "
                    "as the basis for the operational response."
                ),
                "caveats": {},
                "sources": [],
            },
        }

    if decision == "REVIEW_REQUIRED":
        return {
            "packet_id": "EVIDENCE_PACKET::TEST",
            "governance_decision": (
                "REVIEW_REQUIRED"
            ),
            "response_type": "REVIEW",
            "citations_used": [
                "E1"
            ],
            "sections": {
                "evidence_summary": [
                    {
                        "citation_id": "E1",
                        "document_id": "DOC-004",
                        "evidence_text": (
                            "Bed capacity pressure should "
                            "be reviewed alongside site-flow "
                            "and escalation arrangements."
                        ),
                    }
                ],
                "why_human_review_is_required": (
                    "Human review is required before an "
                    "authoritative response is issued."
                ),
                "review_focus": {},
                "evidence_gaps_or_uncertainty": {},
                "sources": [],
            },
        }

    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "citations_used": [],
        "sections": {
            "unable_to_answer_safely": (
                "The system cannot provide a substantive "
                "answer from the approved evidence."
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


def test_auto_answer_links_claim_to_citation():
    linkage = build_claim_citation_links(
        _grounded_response(
            "AUTO_ANSWER"
        ),
        _answer_context(
            "AUTO_ANSWER"
        ),
    )

    claim = linkage[
        "claims"
    ][0]

    assert (
        claim["support_status"]
        == "SUPPORTED"
    )

    assert (
        claim["citation_ids"]
        == ["E1"]
    )


def test_auto_answer_claim_text_is_preserved():
    linkage = build_claim_citation_links(
        _grounded_response(
            "AUTO_ANSWER"
        ),
        _answer_context(
            "AUTO_ANSWER"
        ),
    )

    assert (
        "Bed capacity pressure"
        in linkage[
            "claims"
        ][0][
            "claim_text"
        ]
    )


def test_auto_answer_summary_is_non_substantive():
    linkage = build_claim_citation_links(
        _grounded_response(
            "AUTO_ANSWER"
        ),
        _answer_context(
            "AUTO_ANSWER"
        ),
    )

    statuses = [
        claim[
            "support_status"
        ]
        for claim in linkage[
            "claims"
        ]
    ]

    assert (
        "NON_SUBSTANTIVE"
        in statuses
    )


def test_review_evidence_claim_is_supported():
    linkage = build_claim_citation_links(
        _grounded_response(
            "REVIEW_REQUIRED"
        ),
        _answer_context(
            "REVIEW_REQUIRED"
        ),
    )

    assert (
        linkage[
            "claims"
        ][0][
            "support_status"
        ]
        == "SUPPORTED"
    )


def test_review_statement_is_non_substantive():
    linkage = build_claim_citation_links(
        _grounded_response(
            "REVIEW_REQUIRED"
        ),
        _answer_context(
            "REVIEW_REQUIRED"
        ),
    )

    assert (
        linkage[
            "claims"
        ][1][
            "support_status"
        ]
        == "NON_SUBSTANTIVE"
    )


def test_abstention_has_no_supported_claims():
    linkage = build_claim_citation_links(
        _grounded_response(
            "ABSTAIN"
        ),
        _answer_context(
            "ABSTAIN"
        ),
    )

    assert (
        linkage[
            "linkage_summary"
        ][
            "supported_count"
        ]
        == 0
    )


def test_abstention_claims_are_non_substantive():
    linkage = build_claim_citation_links(
        _grounded_response(
            "ABSTAIN"
        ),
        _answer_context(
            "ABSTAIN"
        ),
    )

    assert all(
        claim[
            "support_status"
        ]
        == "NON_SUBSTANTIVE"
        for claim in linkage[
            "claims"
        ]
    )


def test_packet_id_mismatch_fails_closed():
    response = _grounded_response(
        "AUTO_ANSWER"
    )

    response[
        "packet_id"
    ] = "EVIDENCE_PACKET::OTHER"

    with pytest.raises(
        ValueError,
        match="packet IDs do not match",
    ):
        build_claim_citation_links(
            response,
            _answer_context(
                "AUTO_ANSWER"
            ),
        )


def test_governance_mismatch_fails_closed():
    with pytest.raises(
        ValueError,
        match="governance decisions do not match",
    ):
        build_claim_citation_links(
            _grounded_response(
                "AUTO_ANSWER"
            ),
            _answer_context(
                "REVIEW_REQUIRED"
            ),
        )


def test_response_type_mismatch_fails_closed():
    response = _grounded_response(
        "AUTO_ANSWER"
    )

    response[
        "response_type"
    ] = "REVIEW"

    with pytest.raises(
        ValueError,
        match="response types do not match",
    ):
        build_claim_citation_links(
            response,
            _answer_context(
                "AUTO_ANSWER"
            ),
        )


def test_unknown_response_citation_fails_closed():
    response = _grounded_response(
        "AUTO_ANSWER"
    )

    response[
        "citations_used"
    ] = [
        "E99"
    ]

    with pytest.raises(
        ValueError,
        match="unknown citation ID",
    ):
        build_claim_citation_links(
            response,
            _answer_context(
                "AUTO_ANSWER"
            ),
        )


def test_unknown_claim_citation_fails_closed():
    response = _grounded_response(
        "AUTO_ANSWER"
    )

    response[
        "sections"
    ][
        "evidence_based_explanation"
    ][0][
        "citation_id"
    ] = "E99"

    with pytest.raises(
        ValueError,
        match="Claim references unknown citation ID",
    ):
        build_claim_citation_links(
            response,
            _answer_context(
                "AUTO_ANSWER"
            ),
        )


def test_duplicate_context_citation_id_fails_closed():
    context = _answer_context(
        "AUTO_ANSWER"
    )

    context[
        "citation_index"
    ].append(
        dict(
            context[
                "citation_index"
            ][0]
        )
    )

    with pytest.raises(
        ValueError,
        match="Duplicate citation ID",
    ):
        build_claim_citation_links(
            _grounded_response(
                "AUTO_ANSWER"
            ),
            context,
        )


def test_linkage_summary_counts_claims():
    linkage = build_claim_citation_links(
        _grounded_response(
            "AUTO_ANSWER"
        ),
        _answer_context(
            "AUTO_ANSWER"
        ),
    )

    summary = linkage[
        "linkage_summary"
    ]

    assert (
        summary["claim_count"]
        == 3
    )

    assert (
        summary["supported_count"]
        == 1
    )

    assert (
        summary["non_substantive_count"]
        == 2
    )

    assert (
        summary["unsupported_count"]
        == 0
    )