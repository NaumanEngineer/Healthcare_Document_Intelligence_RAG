import pytest

from src.retrieval.keyword_search import (
    tokenise_text,
    validate_keyword_query,
    filter_keyword_eligible_chunks,
    build_bm25_corpus,
    score_keyword_chunks,
    rank_keyword_results,
    keyword_search,
)


def build_chunk(
    chunk_id: str,
    text: str,
    status: str = "Active",
) -> dict:
    return {
        "chunk_id": chunk_id,
        "document_id": "DOC-008",
        "title": (
            "Ambulance Handover Escalation Guidance"
        ),
        "document_type": (
            "Operational Guidance"
        ),
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": "test.pdf",
        "page": 1,
        "chunk_number": 1,
        "text": text,
    }


def test_tokenise_text():
    result = tokenise_text(
        "Ambulance Handover Delay!"
    )

    assert result == [
        "ambulance",
        "handover",
        "delay",
    ]


def test_validate_keyword_query_accepts_valid_request():
    validate_keyword_query(
        query="ambulance handover",
        top_k=3,
    )


def test_validate_keyword_query_rejects_blank_query():
    with pytest.raises(
        ValueError,
        match="query must be a non-empty string",
    ):
        validate_keyword_query(
            query="   ",
            top_k=3,
        )


def test_filter_keyword_eligible_chunks_blocks_superseded():
    chunks = [
        build_chunk(
            chunk_id="ACTIVE",
            text="ambulance handover delay",
            status="Active",
        ),
        build_chunk(
            chunk_id="OLD",
            text="ambulance handover delay",
            status="Superseded",
        ),
    ]

    result = (
        filter_keyword_eligible_chunks(
            chunks
        )
    )

    assert len(result) == 1
    assert result[0]["chunk_id"] == "ACTIVE"


def test_build_bm25_corpus():
    chunks = [
        build_chunk(
            chunk_id="A",
            text="ambulance handover delay",
        )
    ]

    corpus = build_bm25_corpus(
        chunks
    )

    assert corpus == [
        [
            "ambulance",
            "handover",
            "delay",
        ]
    ]


def test_score_keyword_chunks_adds_score():
    chunks = [
        build_chunk(
            chunk_id="A",
            text="ambulance handover delay",
        ),
        build_chunk(
            chunk_id="B",
            text="bed capacity management",
        ),
    ]

    scored = score_keyword_chunks(
        query="ambulance handover",
        eligible_chunks=chunks,
    )

    assert len(scored) == 2

    assert (
        "keyword_score"
        in scored[0]
    )


def test_rank_keyword_results_orders_highest_score_first():
    scored = [
        {
            "chunk_id": "LOW",
            "keyword_score": 0.2,
        },
        {
            "chunk_id": "HIGH",
            "keyword_score": 2.0,
        },
    ]

    results = (
        rank_keyword_results(
            scored_chunks=scored,
            top_k=2,
        )
    )

    assert (
        results[0]["chunk_id"]
        == "HIGH"
    )

    assert (
        results[0]["keyword_rank"]
        == 1
    )


def test_keyword_search_prefers_exact_ambulance_terms():
    chunks = [
        build_chunk(
            chunk_id="AMBULANCE",
            text=(
                "Ambulance handover delays "
                "should be monitored."
            ),
        ),
        build_chunk(
            chunk_id="WORKFORCE",
            text=(
                "Critical staffing pressure "
                "requires workforce review."
            ),
        ),
    ]

    results = keyword_search(
        query=(
            "ambulance handover delay"
        ),
        chunks=chunks,
        top_k=2,
    )

    assert (
        results[0]["chunk_id"]
        == "AMBULANCE"
    )


def test_keyword_search_returns_empty_when_no_eligible_chunks():
    chunks = [
        build_chunk(
            chunk_id="OLD",
            text="ambulance handover",
            status="Superseded",
        )
    ]

    results = keyword_search(
        query="ambulance handover",
        chunks=chunks,
        top_k=3,
    )

    assert results == []
