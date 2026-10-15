from src.evaluation.citation_assurance import (
    build_citation_assurance,
)


def _answer_context():
    return {
        "context_version": "1.0",
        "packet_id": "PACKET-001",
        "question": "What does the evidence establish?",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citation_index": [
            {
                "citation_id": "E1",
                "evidence_id": "EVIDENCE::DOC-A-C001",
                "document_id": "DOC-A",
                "chunk_id": "DOC-A-C001",
                "page": 1,
                "source_file": "doc_a.txt",
                "version": "1.0",
                "status": "Active",
            },
            {
                "citation_id": "E2",
                "evidence_id": "EVIDENCE::DOC-B-C001",
                "document_id": "DOC-B",
                "chunk_id": "DOC-B-C001",
                "page": 2,
                "source_file": "doc_b.txt",
                "version": "1.0",
                "status": "Active",
            },
        ],
    }


def _single_claim_linkage():
    return {
        "linkage_version": "1.0",
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "claims": [
            {
                "claim_id": "C1",
                "claim_text": (
                    "Operational pressure should be monitored."
                ),
                "section": "evidence_based_explanation",
                "citation_ids": [
                    "E1"
                ],
                "support_status": "SUPPORTED",
            }
        ],
    }


def test_single_source_claim_passes_assurance():
    result = build_citation_assurance(
        _single_claim_linkage(),
        _answer_context(),
        required_citations_by_claim={
            "C1": [
                "E1"
            ]
        },
    )

    assert result[
        "decision"
    ] == "PASS"

    assert result[
        "citation_completeness"
    ][
        "claim_results"
    ][0][
        "status"
    ] == "COMPLETE"


def test_missing_required_second_source_requires_review():
    linkage = _single_claim_linkage()

    linkage[
        "claims"
    ][0][
        "claim_text"
    ] = (
        "The approved evidence contains "
        "conflicting operational positions."
    )

    result = build_citation_assurance(
        linkage,
        _answer_context(),
        required_citations_by_claim={
            "C1": [
                "E1",
                "E2",
            ]
        },
    )

    assert result[
        "decision"
    ] == "REVIEW_REQUIRED"

    assert result[
        "citation_completeness"
    ][
        "claim_results"
    ][0][
        "status"
    ] == "INCOMPLETE"

    assert result[
        "citation_completeness"
    ][
        "claim_results"
    ][0][
        "missing_citation_ids"
    ] == [
        "E2"
    ]


def test_claim_with_two_required_sources_passes():
    linkage = _single_claim_linkage()

    linkage[
        "claims"
    ][0][
        "claim_text"
    ] = (
        "The approved evidence contains "
        "conflicting operational positions."
    )

    linkage[
        "claims"
    ][0][
        "citation_ids"
    ] = [
        "E1",
        "E2",
    ]

    result = build_citation_assurance(
        linkage,
        _answer_context(),
        required_citations_by_claim={
            "C1": [
                "E1",
                "E2",
            ]
        },
    )

    assert result[
        "decision"
    ] == "PASS"


def test_non_substantive_claim_does_not_require_source():
    linkage = _single_claim_linkage()

    linkage[
        "claims"
    ] = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Human review is required before use."
            ),
            "section": "management_summary",
            "citation_ids": [],
            "support_status": "NON_SUBSTANTIVE",
        }
    ]

    result = build_citation_assurance(
        linkage,
        _answer_context(),
    )

    assert result[
        "decision"
    ] == "PASS"

    assert result[
        "citation_completeness"
    ][
        "claim_results"
    ][0][
        "status"
    ] == "NOT_REQUIRED"


def test_unknown_linked_citation_fails_closed():
    linkage = _single_claim_linkage()

    linkage[
        "claims"
    ][0][
        "citation_ids"
    ] = [
        "E99"
    ]

    try:
        build_citation_assurance(
            linkage,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unknown citation ID to fail closed."
        )


def test_duplicate_citation_index_id_fails_closed():
    context = _answer_context()

    context[
        "citation_index"
    ][1][
        "citation_id"
    ] = "E1"

    try:
        build_citation_assurance(
            _single_claim_linkage(),
            context,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate citation IDs to fail closed."
        )


def test_missing_source_metadata_fails_closed():
    context = _answer_context()

    del context[
        "citation_index"
    ][0][
        "source_file"
    ]

    try:
        build_citation_assurance(
            _single_claim_linkage(),
            context,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected missing citation provenance to fail closed."
        )


def test_packet_identity_mismatch_fails_closed():
    linkage = _single_claim_linkage()

    linkage[
        "packet_id"
    ] = "WRONG-PACKET"

    try:
        build_citation_assurance(
            linkage,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected packet mismatch to fail closed."
        )


def test_governance_mismatch_fails_closed():
    linkage = _single_claim_linkage()

    linkage[
        "governance_decision"
    ] = "REVIEW_REQUIRED"

    try:
        build_citation_assurance(
            linkage,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected governance mismatch to fail closed."
        )


def test_response_type_mismatch_fails_closed():
    linkage = _single_claim_linkage()

    linkage[
        "response_type"
    ] = "REVIEW"

    try:
        build_citation_assurance(
            linkage,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected response-type mismatch to fail closed."
        )


def test_abstention_state_is_preserved():
    context = {
        "context_version": "1.0",
        "packet_id": "PACKET-ABSTAIN",
        "question": "What should happen?",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "citation_index": [],
    }

    linkage = {
        "linkage_version": "1.0",
        "packet_id": "PACKET-ABSTAIN",
        "governance_decision": "ABSTAIN",
        "response_type": "ABSTENTION",
        "claims": [
            {
                "claim_id": "C1",
                "claim_text": (
                    "There is insufficient evidence "
                    "to answer safely."
                ),
                "section": "unable_to_answer_safely",
                "citation_ids": [],
                "support_status": "NON_SUBSTANTIVE",
            }
        ],
    }

    result = build_citation_assurance(
        linkage,
        context,
    )

    assert result[
        "decision"
    ] == "ABSTAIN"

    assert result[
        "governance_decision"
    ] == "ABSTAIN"


def test_duplicate_claim_id_fails_closed():
    linkage = _single_claim_linkage()

    linkage[
        "claims"
    ].append(
        dict(
            linkage[
                "claims"
            ][0]
        )
    )

    try:
        build_citation_assurance(
            linkage,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected duplicate claim IDs to fail closed."
        )