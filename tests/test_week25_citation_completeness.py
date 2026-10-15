from src.evaluation.citation_completeness import (
    ABSTAIN,
    COMPLETE,
    INCOMPLETE,
    INVALID_CITATION,
    NOT_REQUIRED,
    PASS,
    REVIEW_REQUIRED,
    UNCITED,
    audit_answer_citation_completeness,
    audit_claim_citation_completeness,
)


def _citation_index():
    return [
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
            "page": 1,
            "source_file": "doc_b.txt",
            "version": "1.0",
            "status": "Active",
        },
    ]


def test_single_source_claim_is_complete():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Ambulance handover delays should be monitored."
        ),
        "citation_ids": [
            "E1"
        ],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        required_citation_ids=[
            "E1"
        ],
    )

    assert result[
        "status"
    ] == COMPLETE

    assert result[
        "missing_citation_ids"
    ] == []


def test_material_claim_without_citation_is_uncited():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational pressure should be monitored."
        ),
        "citation_ids": [],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        required_citation_ids=[
            "E1"
        ],
    )

    assert result[
        "status"
    ] == UNCITED

    assert result[
        "missing_citation_ids"
    ] == [
        "E1"
    ]


def test_unknown_attached_citation_is_invalid():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational pressure should be monitored."
        ),
        "citation_ids": [
            "E99"
        ],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        required_citation_ids=[],
    )

    assert result[
        "status"
    ] == INVALID_CITATION

    assert result[
        "invalid_citation_ids"
    ] == [
        "E99"
    ]


def test_multi_source_claim_missing_second_citation_is_incomplete():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "The approved evidence contains "
            "conflicting operational positions."
        ),
        "citation_ids": [
            "E1"
        ],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        required_citation_ids=[
            "E1",
            "E2",
        ],
    )

    assert result[
        "status"
    ] == INCOMPLETE

    assert result[
        "missing_citation_ids"
    ] == [
        "E2"
    ]


def test_multi_source_claim_with_both_citations_is_complete():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "The approved evidence contains "
            "conflicting operational positions."
        ),
        "citation_ids": [
            "E1",
            "E2",
        ],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        required_citation_ids=[
            "E1",
            "E2",
        ],
    )

    assert result[
        "status"
    ] == COMPLETE

    assert result[
        "attached_citation_ids"
    ] == [
        "E1",
        "E2",
    ]


def test_duplicate_attached_citations_are_normalised():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "The approved evidence contains "
            "conflicting operational positions."
        ),
        "citation_ids": [
            "E1",
            "E1",
            "E2",
        ],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        required_citation_ids=[
            "E1",
            "E2",
        ],
    )

    assert result[
        "status"
    ] == COMPLETE

    assert result[
        "attached_citation_ids"
    ] == [
        "E1",
        "E2",
    ]


def test_non_substantive_claim_does_not_require_citation():
    claim = {
        "claim_id": "C2",
        "claim_text": (
            "Human review is required before use."
        ),
        "citation_ids": [],
    }

    result = audit_claim_citation_completeness(
        claim,
        _citation_index(),
        material=False,
    )

    assert result[
        "status"
    ] == NOT_REQUIRED


def test_answer_passes_when_all_material_claims_complete():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "Operational teams should monitor pressure."
            ),
            "citation_ids": [
                "E1"
            ],
        },
        {
            "claim_id": "C2",
            "claim_text": (
                "Human review is required before use."
            ),
            "citation_ids": [],
        },
    ]

    result = (
        audit_answer_citation_completeness(
            claims,
            _citation_index(),
            required_citations_by_claim={
                "C1": [
                    "E1"
                ]
            },
            non_substantive_claim_ids=[
                "C2"
            ],
        )
    )

    assert result[
        "decision"
    ] == PASS

    assert result[
        "status_counts"
    ][COMPLETE] == 1

    assert result[
        "status_counts"
    ][NOT_REQUIRED] == 1


def test_answer_requires_review_when_multi_source_claim_is_incomplete():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "The approved evidence contains "
                "conflicting operational positions."
            ),
            "citation_ids": [
                "E1"
            ],
        }
    ]

    result = (
        audit_answer_citation_completeness(
            claims,
            _citation_index(),
            required_citations_by_claim={
                "C1": [
                    "E1",
                    "E2",
                ]
            },
        )
    )

    assert result[
        "decision"
    ] == REVIEW_REQUIRED

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == INCOMPLETE


def test_answer_passes_when_multi_source_claim_is_complete():
    claims = [
        {
            "claim_id": "C1",
            "claim_text": (
                "The approved evidence contains "
                "conflicting operational positions."
            ),
            "citation_ids": [
                "E1",
                "E2",
            ],
        }
    ]

    result = (
        audit_answer_citation_completeness(
            claims,
            _citation_index(),
            required_citations_by_claim={
                "C1": [
                    "E1",
                    "E2",
                ]
            },
        )
    )

    assert result[
        "decision"
    ] == PASS

    assert result[
        "claim_results"
    ][0][
        "status"
    ] == COMPLETE


def test_abstain_with_no_material_claims_preserves_abstention():
    result = (
        audit_answer_citation_completeness(
            [],
            [],
            upstream_governance_decision=(
                "ABSTAIN"
            ),
        )
    )

    assert result[
        "decision"
    ] == ABSTAIN


def test_unknown_required_citation_fails_closed():
    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational pressure should be monitored."
        ),
        "citation_ids": [
            "E1"
        ],
    }

    try:
        audit_claim_citation_completeness(
            claim,
            _citation_index(),
            required_citation_ids=[
                "E99"
            ],
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unknown "
            "required citation ID."
        )


def test_duplicate_citation_index_id_fails_closed():
    citation_index = [
        {
            "citation_id": "E1",
        },
        {
            "citation_id": "E1",
        },
    ]

    claim = {
        "claim_id": "C1",
        "claim_text": (
            "Operational pressure should be monitored."
        ),
        "citation_ids": [
            "E1"
        ],
    }

    try:
        audit_claim_citation_completeness(
            claim,
            citation_index,
            required_citation_ids=[
                "E1"
            ],
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for duplicate "
            "citation index ID."
        )