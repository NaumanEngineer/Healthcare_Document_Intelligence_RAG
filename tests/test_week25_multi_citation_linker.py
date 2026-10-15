from src.generation.claim_citation_linker import (
    build_claim_citation_links,
)


def _answer_context(
    governance_decision="AUTO_ANSWER",
    response_type="ANSWER",
):
    return {
        "context_version": "1.0",
        "packet_id": "PACKET-001",
        "question": (
            "What does the evidence establish?"
        ),
        "governance_decision": (
            governance_decision
        ),
        "response_type": response_type,
        "citation_index": [
            {
                "citation_id": "E1",
                "evidence_id": (
                    "EVIDENCE::DOC-A-C001"
                ),
                "document_id": "DOC-A",
                "chunk_id": "DOC-A-C001",
                "page": 1,
                "source_file": "doc_a.txt",
                "version": "1.0",
                "status": "Active",
            },
            {
                "citation_id": "E2",
                "evidence_id": (
                    "EVIDENCE::DOC-B-C001"
                ),
                "document_id": "DOC-B",
                "chunk_id": "DOC-B-C001",
                "page": 2,
                "source_file": "doc_b.txt",
                "version": "1.0",
                "status": "Active",
            },
        ],
    }


def test_legacy_single_citation_answer_still_works():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1"
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "Operational pressure "
                        "should be monitored."
                    ),
                    "citation_id": "E1",
                }
            ]
        },
    }

    result = build_claim_citation_links(
        response,
        _answer_context(),
    )

    assert result[
        "claims"
    ][0][
        "citation_ids"
    ] == [
        "E1"
    ]


def test_answer_claim_can_preserve_two_citations():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1",
            "E2",
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "The approved evidence "
                        "contains conflicting "
                        "operational positions."
                    ),
                    "citation_ids": [
                        "E1",
                        "E2",
                    ],
                }
            ]
        },
    }

    result = build_claim_citation_links(
        response,
        _answer_context(),
    )

    assert result[
        "claims"
    ][0][
        "citation_ids"
    ] == [
        "E1",
        "E2",
    ]

    assert result[
        "safety_summary"
    ][
        "multi_citation_claims_supported"
    ] is True


def test_review_claim_can_preserve_two_citations():
    context = _answer_context(
        governance_decision=(
            "REVIEW_REQUIRED"
        ),
        response_type="REVIEW",
    )

    response = {
        "packet_id": "PACKET-001",
        "governance_decision": (
            "REVIEW_REQUIRED"
        ),
        "response_type": "REVIEW",
        "citations_used": [
            "E1",
            "E2",
        ],
        "sections": {
            "evidence_summary": [
                {
                    "evidence_text": (
                        "The approved evidence "
                        "contains conflicting "
                        "operational positions."
                    ),
                    "citation_ids": [
                        "E1",
                        "E2",
                    ],
                }
            ],
            "why_human_review_is_required": (
                "The evidence conflict "
                "requires human review."
            ),
        },
    }

    result = build_claim_citation_links(
        response,
        context,
    )

    assert result[
        "claims"
    ][0][
        "citation_ids"
    ] == [
        "E1",
        "E2",
    ]

    assert result[
        "claims"
    ][1][
        "support_status"
    ] == "NON_SUBSTANTIVE"


def test_duplicate_multi_citations_are_normalised():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1",
            "E2",
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "The evidence uses "
                        "two approved sources."
                    ),
                    "citation_ids": [
                        "E1",
                        "E1",
                        "E2",
                    ],
                }
            ]
        },
    }

    result = build_claim_citation_links(
        response,
        _answer_context(),
    )

    assert result[
        "claims"
    ][0][
        "citation_ids"
    ] == [
        "E1",
        "E2",
    ]


def test_unknown_multi_citation_fails_closed():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1"
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "The evidence conflicts."
                    ),
                    "citation_ids": [
                        "E1",
                        "E99",
                    ],
                }
            ]
        },
    }

    try:
        build_claim_citation_links(
            response,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected unknown multi-citation "
            "identifier to fail closed."
        )


def test_empty_multi_citation_list_fails_closed():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "Operational pressure "
                        "should be monitored."
                    ),
                    "citation_ids": [],
                }
            ]
        },
    }

    try:
        build_claim_citation_links(
            response,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected empty citation_ids "
            "to fail closed."
        )


def test_conflicting_singular_and_plural_forms_fail():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1",
            "E2",
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "The evidence conflicts."
                    ),
                    "citation_id": "E1",
                    "citation_ids": [
                        "E2"
                    ],
                }
            ]
        },
    }

    try:
        build_claim_citation_links(
            response,
            _answer_context(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected conflicting citation "
            "forms to fail closed."
        )


def test_consistent_singular_and_plural_forms_allowed():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1",
            "E2",
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "The evidence conflicts."
                    ),
                    "citation_id": "E1",
                    "citation_ids": [
                        "E1",
                        "E2",
                    ],
                }
            ]
        },
    }

    result = build_claim_citation_links(
        response,
        _answer_context(),
    )

    assert result[
        "claims"
    ][0][
        "citation_ids"
    ] == [
        "E1",
        "E2",
    ]


def test_management_summary_remains_non_substantive():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1"
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "Operational pressure "
                        "should be monitored."
                    ),
                    "citation_id": "E1",
                }
            ],
            "management_summary": (
                "The evidence has been "
                "summarised for review."
            ),
        },
    }

    result = build_claim_citation_links(
        response,
        _answer_context(),
    )

    assert result[
        "claims"
    ][1][
        "citation_ids"
    ] == []

    assert result[
        "claims"
    ][1][
        "support_status"
    ] == "NON_SUBSTANTIVE"


def test_linked_citation_summary_preserves_both_sources():
    response = {
        "packet_id": "PACKET-001",
        "governance_decision": "AUTO_ANSWER",
        "response_type": "ANSWER",
        "citations_used": [
            "E1",
            "E2",
        ],
        "sections": {
            "evidence_based_explanation": [
                {
                    "evidence_text": (
                        "The approved evidence "
                        "contains conflicting "
                        "operational positions."
                    ),
                    "citation_ids": [
                        "E1",
                        "E2",
                    ],
                }
            ]
        },
    }

    result = build_claim_citation_links(
        response,
        _answer_context(),
    )

    assert result[
        "linked_citation_ids"
    ] == [
        "E1",
        "E2",
    ]

    assert result[
        "linkage_summary"
    ][
        "linked_citation_count"
    ] == 2