import pytest

from src.retrieval.embeddings import (
    create_text_hash,
)

from src.retrieval.semantic_search import (
    validate_query,
    validate_embedding_freshness,
    select_final_results,
)

from src.retrieval.reranker import (
    rerank_candidates,
)

from src.evaluation.retrieval_qa import (
    active_only_success,
    build_retrieval_qa_result,
)


def build_result(
    chunk_id: str = "DOC-001-V1.0-P001-C001",
    status: str = "Active",
    similarity_score: float = 0.80,
) -> dict:
    text = "Operational escalation guidance."

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
        "text": text,
        "vector": [0.1, 0.2, 0.3],
        "embedding_model": "test-model",
        "embedding_dimensions": 3,
        "text_hash": create_text_hash(text),
        "similarity_score": similarity_score,
    }


def test_validate_query_accepts_similarity_threshold():
    validate_query(
        query="What is the escalation process?",
        candidate_k=10,
        final_k=3,
        min_similarity=0.40,
    )


def test_validate_query_rejects_invalid_similarity_threshold():
    with pytest.raises(ValueError):
        validate_query(
            query="test",
            candidate_k=10,
            final_k=3,
            min_similarity=1.5,
        )


def test_embedding_freshness_passes_when_text_unchanged():
    chunk = build_result()

    validate_embedding_freshness(
        chunk
    )


def test_embedding_freshness_rejects_stale_embedding():
    chunk = build_result()

    chunk["text"] = (
        "The policy text has changed after embedding."
    )

    with pytest.raises(
        ValueError,
        match="Stale embedding",
    ):
        validate_embedding_freshness(
            chunk
        )


def test_reranker_orders_higher_similarity_first():
    low = build_result(
        chunk_id="LOW",
        similarity_score=0.40,
    )

    high = build_result(
        chunk_id="HIGH",
        similarity_score=0.90,
    )

    results = rerank_candidates(
        [low, high]
    )

    assert results[0]["chunk_id"] == "HIGH"
    assert results[0]["rerank_rank"] == 1


def test_similarity_threshold_removes_weak_evidence():
    weak = build_result(
        chunk_id="WEAK",
        similarity_score=0.30,
    )

    strong = build_result(
        chunk_id="STRONG",
        similarity_score=0.85,
    )

    results = select_final_results(
        candidates=[strong, weak],
        final_k=3,
        min_similarity=0.50,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "STRONG"


def test_similarity_threshold_can_return_no_evidence():
    weak = build_result(
        similarity_score=0.20,
    )

    results = select_final_results(
        candidates=[weak],
        final_k=3,
        min_similarity=0.50,
    )

    assert results == []


def test_empty_results_are_not_marked_active_success():
    assert active_only_success([]) is None


def test_qa_report_identifies_no_results():
    report = build_retrieval_qa_result(
        query_id="Q006",
        results=[],
    )

    assert report["no_results"] is True
    assert report["active_only"] is None


def test_active_results_pass_active_only_control():
    result = build_result()

    assert active_only_success(
        [result]
    ) is True


def test_superseded_result_fails_active_only_control():
    result = build_result(
        status="Superseded"
    )

    assert active_only_success(
        [result]
    ) is False
