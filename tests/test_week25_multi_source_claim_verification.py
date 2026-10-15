from src.evaluation.multi_source_claim_verification import (
    CITATION_MISMATCH,
    PARTIALLY_SUPPORTED,
    SUPPORTED,
    UNSUPPORTED,
    verify_multi_source_relationship_claim,
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
            "page": 2,
            "source_file": "doc_b.txt",
            "version": "1.0",
            "status": "Active",
        },
    ]


def _evidence():
    return {
        "E1": {
            "evidence_id": "EVIDENCE::DOC-A-C001",
            "document_id": "DOC-A",
            "chunk_id": "DOC-A-C001",
            "status": "Active",
            "evidence_text": (
                "DOC-A conflicts with DOC-B regarding "
                "the operational escalation approach."
            ),
        },
        "E2": {
            "evidence_id": "EVIDENCE::DOC-B-C001",
            "document_id": "DOC-B",
            "chunk_id": "DOC-B-C001",
            "status": "Active",
            "evidence_text": (
                "DOC-B conflicts with DOC-A regarding "
                "the operational escalation approach."
            ),
        },
    }


def _conflict_precedence():
    return {
        "decision": "BLOCK_COMBINATION",
        "relationship_checks": [
            {
                "document_ids": [
                    "DOC-A",
                    "DOC-B",
                ],
                "relationship_type": "CONFLICT",
                "decision": "RELATIONSHIP_SUPPORTED",
            }
        ],
    }


def _claim():
    return {
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


def test_complete_conflict_claim_is_supported():
    result = (
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            _evidence(),
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == SUPPORTED

    assert result[
        "evidence_count"
    ] == 2


def test_missing_second_source_is_partial():
    claim = _claim()

    claim[
        "citation_ids"
    ] = [
        "E1"
    ]

    result = (
        verify_multi_source_relationship_claim(
            claim,
            _citation_index(),
            _evidence(),
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == PARTIALLY_SUPPORTED

    assert result[
        "missing_citation_ids"
    ] == [
        "E2"
    ]


def test_unknown_attached_citation_is_mismatch():
    claim = _claim()

    claim[
        "citation_ids"
    ] = [
        "E1",
        "E99",
    ]

    result = (
        verify_multi_source_relationship_claim(
            claim,
            _citation_index(),
            _evidence(),
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == CITATION_MISMATCH


def test_missing_evidence_resolution_is_mismatch():
    evidence = _evidence()

    del evidence[
        "E2"
    ]

    result = (
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            evidence,
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == CITATION_MISMATCH


def test_document_identity_mismatch_fails():
    evidence = _evidence()

    evidence[
        "E2"
    ][
        "document_id"
    ] = "WRONG-DOC"

    result = (
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            evidence,
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == CITATION_MISMATCH


def test_non_active_evidence_fails_closed():
    evidence = _evidence()

    evidence[
        "E2"
    ][
        "status"
    ] = "Superseded"

    result = (
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            evidence,
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == CITATION_MISMATCH


def test_wrong_precedence_decision_is_unsupported():
    precedence = _conflict_precedence()

    precedence[
        "decision"
    ] = "SAFE_TO_COMBINE"

    result = (
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            _evidence(),
            precedence,
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == UNSUPPORTED


def test_missing_explicit_relationship_is_unsupported():
    precedence = {
        "decision": "BLOCK_COMBINATION",
        "relationship_checks": [],
    }

    result = (
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            _evidence(),
            precedence,
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == UNSUPPORTED


def test_claim_must_assert_relationship():
    claim = _claim()

    claim[
        "claim_text"
    ] = (
        "Operational teams should "
        "monitor pressure."
    )

    result = (
        verify_multi_source_relationship_claim(
            claim,
            _citation_index(),
            _evidence(),
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1",
                "E2",
            ],
        )
    )

    assert result[
        "status"
    ] == UNSUPPORTED


def test_multi_source_requires_two_required_citations():
    try:
        verify_multi_source_relationship_claim(
            _claim(),
            _citation_index(),
            _evidence(),
            _conflict_precedence(),
            relationship_type="CONFLICT",
            required_citation_ids=[
                "E1"
            ],
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected multi-source verification "
            "to require at least two citations."
        )