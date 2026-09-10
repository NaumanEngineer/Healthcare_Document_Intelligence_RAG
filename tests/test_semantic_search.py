import pytest

from src.retrieval.semantic_search import (
    validate_query,
    cosine_similarity,
    filter_eligible_chunks,
    rank_candidates,
)


def build_chunk(
    chunk_id: str,
    status: str = "Active",
    score_vector: list[float] | None = None,
) -> dict:
    return {
        "chunk_id": chunk_id,
        "document_id": "DOC-001",
        "title": "Operational Escalation Policy",
        "document_type": "Operational Policy",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": "policy.pdf",
        "page": 1,
        "chunk_number": 1,
        "text": "Operational escalation guidance.",
        "vector": (
            score_vector
            if score_vector is not None
            else [0.1, 0.2, 0.3]
        ),
        "embedding_model": "test-model",
        "embedding_dimensions": 3,
        "text_hash": "abc123",
    }


def test_validate_query_accepts_valid_request():
    validate_query(
        query="What is the escalation policy?",
        candidate_k=10,
        final_k=3,
    )


def test_validate_query_rejects_empty_query():
    with pytest.raises(ValueError):
        validate_query(
            query="",
            candidate_k=10,
            final_k=3,
        )


def test_final_k_cannot_exceed_candidate_k():
    with pytest.raises(ValueError):
        validate_query(
            query="test",
            candidate_k=2,
            final_k=3,
        )


def test_cosine_similarity_identical_vectors():
    result = cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    )

    assert result == pytest.approx(
        1.0
    )


def test_cosine_similarity_rejects_dimension_mismatch():
    with pytest.raises(ValueError):
        cosine_similarity(
            [1.0, 0.0],
            [1.0, 0.0, 0.0],
        )


def test_filter_eligible_chunks_excludes_superseded():
    chunks = [
        build_chunk(
            "DOC-001-V1.0-P001-C001",
            status="Active",
        ),
        {
            **build_chunk(
                "DOC-002-V1.0-P001-C001",
                status="Superseded",
            ),
            "document_id": "DOC-002",
        },
    ]

    eligible = filter_eligible_chunks(
        chunks
    )

    assert len(eligible) == 1
    assert eligible[0]["status"] == "Active"


def test_rank_candidates_orders_highest_score_first():
    chunks = [
        {
            "chunk_id": "LOW",
            "similarity_score": 0.4,
        },
        {
            "chunk_id": "HIGH",
            "similarity_score": 0.9,
        },
    ]

    ranked = rank_candidates(
        scored_chunks=chunks,
        candidate_k=2,
    )

    assert ranked[0]["chunk_id"] == "HIGH"
    assert ranked[0]["candidate_rank"] == 1
