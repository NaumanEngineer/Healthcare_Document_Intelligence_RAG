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
