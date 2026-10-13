from __future__ import annotations

import pytest

from src.generation.claim_citation_linker import (
    build_claim_citation_links,
)


def _context() -> dict:
    return {
        "context_version": "1.0",
        "packet_id": "EVIDENCE_PACKET::TEST",
        "question": "Test question",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
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
    }


def _response() -> dict:
    return {
        "packet_id": "EVIDENCE_PACKET::TEST",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1"
        ],
        "sections": {
            "management_summary": (
                "Approved evidence is available."
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
                "Use the approved evidence above."
            ),
            "caveats": {},
            "sources": [],
        },
    }


def test_supported_claim_remains_supported():
    linkage = build_claim_citation_links(
        _response(),
        _context(),
    )

    assert (
        linkage["claims"][0]["support_status"]
        == "SUPPORTED"
    )

    assert (
        linkage["unsupported_claims"]
        == []
    )


def test_unknown_citation_cannot_be_treated_as_supported():
    response = _response()

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
            _context(),
        )


def test_response_level_unknown_citation_fails_closed():
    response = _response()

    response[
        "citations_used"
    ].append(
        "E99"
    )

    with pytest.raises(
        ValueError,
        match="unknown citation ID",
    ):
        build_claim_citation_links(
            response,
            _context(),
        )


def test_blank_claim_text_fails_closed():
    response = _response()

    response[
        "sections"
    ][
        "evidence_based_explanation"
    ][0][
        "evidence_text"
    ] = "   "

    with pytest.raises(
        ValueError,
        match="must not be blank",
    ):
        build_claim_citation_links(
            response,
            _context(),
        )


def test_blank_claim_citation_fails_closed():
    response = _response()

    response[
        "sections"
    ][
        "evidence_based_explanation"
    ][0][
        "citation_id"
    ] = "   "

    with pytest.raises(
        ValueError,
        match="must not be blank",
    ):
        build_claim_citation_links(
            response,
            _context(),
        )


def test_duplicate_context_citation_fails_closed():
    context = _context()

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
            _response(),
            context,
        )