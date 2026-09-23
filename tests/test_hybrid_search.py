from copy import deepcopy
import importlib

import pytest

from src.retrieval.reranker import rerank_candidates, rerank_hybrid_candidates

from src.retrieval.hybrid_search import (
    reciprocal_rank_contribution,
    build_result_key,
    fuse_ranked_results,
    select_hybrid_results,
)


def build_result(
    chunk_id: str,
    document_id: str,
    status: str = "Active",
) -> dict:
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "title": "Synthetic Operational Guidance",
        "document_type": "Operational Guidance",
        "source_type": "Synthetic",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "status": status,
        "source_file": "test.pdf",
        "page": 1,
        "chunk_number": 1,
        "text": "Operational guidance text.",
    }


def test_rrf_higher_rank_has_higher_contribution():
    rank_one = (
        reciprocal_rank_contribution(
            rank=1,
        )
    )

    rank_three = (
        reciprocal_rank_contribution(
            rank=3,
        )
    )

    assert rank_one > rank_three


def test_build_result_key_uses_chunk_id():
    result = build_result(
        chunk_id="CHUNK-001",
        document_id="DOC-001",
    )

    assert (
        build_result_key(result)
        == "CHUNK-001"
    )


def test_fusion_rewards_result_present_in_both_lists():
    shared = build_result(
        chunk_id="SHARED",
        document_id="DOC-008",
    )

    semantic_only = build_result(
        chunk_id="SEMANTIC",
        document_id="DOC-012",
    )

    keyword_only = build_result(
        chunk_id="KEYWORD",
        document_id="DOC-007",
    )

    fused = fuse_ranked_results(
        semantic_results=[
            shared,
            semantic_only,
        ],
        keyword_results=[
            shared,
            keyword_only,
        ],
    )

    assert (
        fused[0]["chunk_id"]
        == "SHARED"
    )

    assert (
        fused[0]["semantic_rank"]
        == 1
    )

    assert (
        fused[0]["keyword_rank"]
        == 1
    )


def test_fusion_preserves_semantic_only_result():
    semantic = build_result(
        chunk_id="SEMANTIC",
        document_id="DOC-012",
    )

    fused = fuse_ranked_results(
        semantic_results=[
            semantic
        ],
        keyword_results=[],
    )

    assert len(fused) == 1

    assert (
        fused[0]["semantic_rank"]
        == 1
    )

    assert (
        fused[0]["keyword_rank"]
        is None
    )


def test_fusion_preserves_keyword_only_result():
    keyword = build_result(
        chunk_id="KEYWORD",
        document_id="DOC-008",
    )

    fused = fuse_ranked_results(
        semantic_results=[],
        keyword_results=[
            keyword
        ],
    )

    assert len(fused) == 1

    assert (
        fused[0]["semantic_rank"]
        is None
    )

    assert (
        fused[0]["keyword_rank"]
        == 1
    )


def test_select_hybrid_results_blocks_superseded():
    active = build_result(
        chunk_id="ACTIVE",
        document_id="DOC-001",
        status="Active",
    )

    active["rrf_score"] = 0.03

    superseded = build_result(
        chunk_id="OLD",
        document_id="DOC-001",
        status="Superseded",
    )

    superseded[
        "rrf_score"
    ] = 0.10

    results = select_hybrid_results(
        fused_results=[
            superseded,
            active,
        ],
        final_k=3,
    )

    assert len(results) == 1

    assert (
        results[0]["chunk_id"]
        == "ACTIVE"
    )


def test_select_hybrid_results_applies_threshold():
    strong = build_result(
        chunk_id="STRONG",
        document_id="DOC-008",
    )

    strong[
        "rrf_score"
    ] = 0.05

    weak = build_result(
        chunk_id="WEAK",
        document_id="DOC-012",
    )

    weak[
        "rrf_score"
    ] = 0.01

    results = select_hybrid_results(
        fused_results=[
            strong,
            weak,
        ],
        final_k=3,
        min_rrf_score=0.02,
    )

    assert len(results) == 1

    assert (
        results[0]["chunk_id"]
        == "STRONG"
    )


@pytest.mark.parametrize("similarity", [None, 0.1])
def test_q027_hybrid_reranker_preserves_weather_rrf_signal(similarity):
    ambulance = {
        "chunk_id": "DOC-008-C001", "document_id": "DOC-008",
        "status": "Active", "similarity_score": 0.99, "rrf_score": 0.02,
    }
    weather = {
        "chunk_id": "DOC-009-C001", "document_id": "DOC-009",
        "status": "Active", "rrf_score": 0.03,
        "semantic_rank": None, "keyword_rank": 1,
        "semantic_rrf_contribution": 0.0, "keyword_rrf_contribution": 0.03,
    }
    if similarity is not None:
        weather["similarity_score"] = similarity
    candidates = [ambulance, weather]
    before = deepcopy(candidates)
    results = rerank_hybrid_candidates(candidates)
    assert [r["document_id"] for r in results] == ["DOC-009", "DOC-008"]
    assert [r["hybrid_rerank_rank"] for r in results] == [1, 2]
    assert results[0] == {**weather, "hybrid_rerank_rank": 1}
    assert candidates == before


@pytest.mark.parametrize("status", ["Draft", "Superseded", "Archived"])
def test_hybrid_reranker_prefers_active_status(status):
    results = rerank_hybrid_candidates([
        {"chunk_id": "OLD", "status": status, "rrf_score": 0.9},
        {"chunk_id": "ACTIVE", "status": "Active", "rrf_score": 0.01},
    ])
    assert results[0]["chunk_id"] == "ACTIVE"


def test_hybrid_reranker_breaks_rrf_ties_by_chunk_id_not_similarity():
    candidates = [
        {"chunk_id": "A", "status": "Active", "rrf_score": 0.02, "similarity_score": 0.99},
        {"chunk_id": "B", "status": "Active", "rrf_score": 0.02},
    ]
    expected = rerank_hybrid_candidates(candidates)
    assert [r["chunk_id"] for r in expected] == ["B", "A"]
    assert rerank_hybrid_candidates(list(reversed(candidates))) == expected


def test_semantic_reranker_still_uses_similarity_and_original_rank_field():
    candidates = [
        {"chunk_id": "Z", "status": "Draft", "similarity_score": 1.0, "rrf_score": 1.0},
        {"chunk_id": "C", "status": "Active", "similarity_score": 0.1, "rrf_score": 0.9},
        {"chunk_id": "A", "status": "Active", "similarity_score": 0.8, "rrf_score": 0.01},
        {"chunk_id": "B", "status": "Active", "similarity_score": 0.8, "rrf_score": 0.01},
    ]
    before = deepcopy(candidates)
    results = rerank_candidates(candidates)
    assert [r["chunk_id"] for r in results] == ["B", "A", "C", "Z"]
    assert [r["rerank_rank"] for r in results] == [1, 2, 3, 4]
    assert all("hybrid_rerank_rank" not in r for r in results)
    assert candidates == before


def test_hybrid_reranker_handles_empty_input_and_rejects_non_list():
    assert rerank_hybrid_candidates([]) == []
    with pytest.raises(TypeError, match="candidates must be a list"):
        rerank_hybrid_candidates({})


def test_default_hybrid_search_preserves_semantic_reranking(monkeypatch):
    module = importlib.import_module("src.retrieval.hybrid_search")
    semantic = [
        {**build_result(f"DOC-008-C00{i}", "DOC-008"), "similarity_score": 0.99 - i / 100}
        for i in range(1, 4)
    ]
    weather = build_result("DOC-009-C001", "DOC-009")
    keyword = [weather, semantic[0]]
    monkeypatch.setattr(module, "semantic_search", lambda **kwargs: semantic)
    monkeypatch.setattr(module, "keyword_search", lambda **kwargs: keyword)
    fused = fuse_ranked_results(semantic, keyword)
    results = module.hybrid_search(
        query="How should severe weather pressure and ambulance handover disruption be considered together?",
        chunks=[], embedded_chunks=[], model=None, embedding_model="test", final_k=2,
    )
    assert [r["document_id"] for r in results] == ["DOC-008", "DOC-008"]
    assert [r["rerank_rank"] for r in results] == [1, 2]
    for result in results:
        original = next(r for r in fused if r["chunk_id"] == result["chunk_id"])
        for field in ("semantic_rank", "keyword_rank", "semantic_rrf_contribution",
                      "keyword_rrf_contribution", "rrf_score"):
            assert result[field] == original[field]
