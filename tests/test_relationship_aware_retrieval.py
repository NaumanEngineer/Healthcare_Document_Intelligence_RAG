from __future__ import annotations

import pytest

import src.retrieval.relationship_aware_retrieval as relationship_module

from src.retrieval.relationship_aware_retrieval import (
    expand_results_with_relationships,
)


def make_chunk(
    chunk_id: str,
    document_id: str,
    *,
    status: str = "Active",
    text: str = "Synthetic operational evidence.",
) -> dict:
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "title": f"Title {document_id}",
        "document_type": "Procedure",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": f"{document_id}.txt",
        "page": 1,
        "chunk_number": 1,
        "text": text,
    }


def relationship_record(
    *,
    source_document_id: str = "DOC-011",
    relationship_type: str = "COMPLEMENTS",
    target_document_id: str = "DOC-003",
    evidence_document_id: str = "DOC-011",
    queried_document_id: str = "DOC-011",
    related_document_id: str = "DOC-003",
    retrieval_direction: str = "OUTBOUND",
) -> dict:
    return {
        "source_document_id": source_document_id,
        "relationship_type": relationship_type,
        "target_document_id": target_document_id,
        "evidence_document_id": evidence_document_id,
        "queried_document_id": queried_document_id,
        "related_document_id": related_document_id,
        "retrieval_direction": retrieval_direction,
    }


def test_relationship_expansion_adds_related_document_chunks(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
        make_chunk(
            "DOC-003-C2",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        max_related_chunks=2,
    )

    assert result["audit"]["stop_reason"] == (
        "RELATED_EVIDENCE_ADDED"
    )

    assert result["audit"][
        "relationship_evidence_candidate_ids"
    ] == []

    assert result["audit"][
        "related_candidate_ids"
    ] == [
        "DOC-003-C1",
        "DOC-003-C2",
    ]

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-003-C1",
        "DOC-003-C2",
    ]

    assert len(result["results"]) == 3


def test_relationship_expansion_respects_limit(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
        make_chunk(
            "DOC-003-C2",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        max_related_chunks=1,
    )

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-003-C1"
    ]

    assert len(result["results"]) == 2


def test_relationship_evidence_chunk_is_prioritised(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
            text=(
                "Critical staffing risk and operational "
                "pressure."
            ),
        )
    ]

    evidence_chunk = make_chunk(
        "DOC-011-C2",
        "DOC-011",
        text=(
            "This contingency procedure complements "
            "the Workforce Escalation Procedure."
        ),
    )

    related_chunk = make_chunk(
        "DOC-003-C1",
        "DOC-003",
    )

    chunks = [
        *initial,
        related_chunk,
        evidence_chunk,
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        max_related_chunks=2,
    )

    assert result["audit"][
        "relationship_evidence_candidate_ids"
    ] == [
        "DOC-011-C2"
    ]

    assert result["audit"][
        "related_candidate_ids"
    ] == [
        "DOC-003-C1"
    ]

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-011-C2",
        "DOC-003-C1",
    ]


def test_existing_related_document_is_not_added_again(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        ),
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C2",
            "DOC-003",
        ),
    ]

    def fake_relationships(
        document_id,
        active_only=True,
    ):
        if document_id == "DOC-011":
            return [
                relationship_record(
                    queried_document_id="DOC-011",
                    related_document_id="DOC-003",
                    retrieval_direction="OUTBOUND",
                )
            ]

        if document_id == "DOC-003":
            return [
                relationship_record(
                    queried_document_id="DOC-003",
                    related_document_id="DOC-011",
                    retrieval_direction=(
                        "INBOUND_SYMMETRIC"
                    ),
                )
            ]

        return []

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        fake_relationships,
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
    )

    assert result["audit"][
        "relationship_evidence_candidate_ids"
    ] == []

    assert result["audit"][
        "related_candidate_ids"
    ] == []

    assert result["audit"][
        "accepted_chunk_ids"
    ] == []

    assert result["audit"]["stop_reason"] == (
        "NO_ELIGIBLE_RELATED_CHUNKS"
    )


def test_non_active_related_chunk_is_excluded(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-014-C1",
            "DOC-014",
            status="Draft",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record(
                target_document_id="DOC-014",
                related_document_id="DOC-014",
            )
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
    )

    assert result["audit"][
        "accepted_chunk_ids"
    ] == []

    assert result["audit"]["stop_reason"] == (
        "NO_ELIGIBLE_RELATED_CHUNKS"
    )


def test_zero_expansion_limit_preserves_initial_results():
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    result = expand_results_with_relationships(
        initial,
        initial,
        max_related_chunks=0,
    )

    assert result["results"] == initial

    assert result["audit"]["expansion_count"] == 0

    assert result["audit"]["stop_reason"] == (
        "NO_EXPANSION_REQUESTED"
    )


def test_empty_initial_results_stop_safely():
    chunks = [
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        )
    ]

    result = expand_results_with_relationships(
        [],
        chunks,
    )

    assert result["results"] == []

    assert result["audit"]["stop_reason"] == (
        "NO_INITIAL_ACTIVE_RESULTS"
    )


def test_relationship_type_filter_applied(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        relationship_type="CONFLICT",
    )

    assert result["audit"][
        "accepted_chunk_ids"
    ] == []

    assert result["audit"]["stop_reason"] == (
        "NO_RELATED_DOCUMENTS"
    )


def test_relationship_type_filter_normalises_case(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        relationship_type=" complements ",
    )

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-003-C1"
    ]


def test_duplicate_chunk_not_added():
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
    ]

    result = expand_results_with_relationships(
        initial,
        chunks,
    )

    chunk_ids = [
        item["chunk_id"]
        for item in result["results"]
    ]

    assert len(chunk_ids) == len(
        set(chunk_ids)
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        -1,
        True,
        False,
        1.5,
        "2",
        None,
    ],
)
def test_invalid_max_related_chunks_rejected(
    invalid_value,
):
    with pytest.raises(
        (TypeError, ValueError)
    ):
        expand_results_with_relationships(
            [],
            [],
            max_related_chunks=invalid_value,
        )


def test_results_must_be_list():
    with pytest.raises(TypeError):
        expand_results_with_relationships(
            {},
            [],
        )


def test_chunks_must_be_list():
    with pytest.raises(TypeError):
        expand_results_with_relationships(
            [],
            {},
        )


def test_result_items_must_be_dictionaries():
    with pytest.raises(TypeError):
        expand_results_with_relationships(
            [
                "not-a-dict",
            ],
            [],
        )


def test_chunk_items_must_be_dictionaries():
    with pytest.raises(TypeError):
        expand_results_with_relationships(
            [],
            [
                "not-a-dict",
            ],
        )


def test_relationship_type_must_be_string_or_none():
    with pytest.raises(TypeError):
        expand_results_with_relationships(
            [],
            [],
            relationship_type=123,
        )


def test_audit_records_relationship_metadata(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    record = relationship_record()

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            record
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
    )

    assert result["audit"][
        "relationship_records"
    ] == [
        record
    ]


def test_related_candidate_canonical_order_is_preserved(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C2",
            "DOC-003",
        ),
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        max_related_chunks=2,
    )

    assert result["audit"][
        "relationship_evidence_candidate_ids"
    ] == []

    assert result["audit"][
        "related_candidate_ids"
    ] == [
        "DOC-003-C2",
        "DOC-003-C1",
    ]

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-003-C2",
        "DOC-003-C1",
    ]


def test_relationship_evidence_priority_respects_limit(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
        make_chunk(
            "DOC-011-C2",
            "DOC-011",
            text=(
                "This contingency procedure complements "
                "the Workforce Escalation Procedure."
            ),
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
        max_related_chunks=1,
    )

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-011-C2"
    ]

    assert result["audit"][
        "related_candidate_ids"
    ] == [
        "DOC-003-C1"
    ]


def test_non_matching_text_is_not_relationship_evidence(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-011-C2",
            "DOC-011",
            text=(
                "This document discusses workforce "
                "contingency arrangements."
            ),
        ),
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
    )

    assert result["audit"][
        "relationship_evidence_candidate_ids"
    ] == []

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-003-C1"
    ]


def test_evidence_chunk_must_be_active(
    monkeypatch,
):
    initial = [
        make_chunk(
            "DOC-011-C1",
            "DOC-011",
        )
    ]

    chunks = [
        *initial,
        make_chunk(
            "DOC-011-C2",
            "DOC-011",
            status="Draft",
            text=(
                "This contingency procedure complements "
                "the Workforce Escalation Procedure."
            ),
        ),
        make_chunk(
            "DOC-003-C1",
            "DOC-003",
        ),
    ]

    monkeypatch.setattr(
        relationship_module,
        "get_relationships_for_document",
        lambda document_id, active_only=True: [
            relationship_record()
        ],
    )

    result = expand_results_with_relationships(
        initial,
        chunks,
    )

    assert result["audit"][
        "relationship_evidence_candidate_ids"
    ] == []

    assert result["audit"][
        "accepted_chunk_ids"
    ] == [
        "DOC-003-C1"
    ]