from __future__ import annotations

from src.retrieval.semantic_search import (
    semantic_search,
)

from src.retrieval.keyword_search import (
    keyword_search,
)

from src.retrieval.hybrid_search import (
    DEFAULT_RRF_K,
    validate_hybrid_query,
    fuse_ranked_results,
    select_hybrid_results,
)


def hybrid_search_rrf_only(
    query: str,
    chunks: list[dict],
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    semantic_k: int = 10,
    keyword_k: int = 10,
    final_k: int = 3,
    semantic_min_similarity: float | None = None,
    keyword_min_score: float | None = None,
    min_rrf_score: float | None = None,
    rrf_k: int = DEFAULT_RRF_K,
) -> list[dict]:
    """
    Hybrid retrieval experiment that preserves
    Reciprocal Rank Fusion ordering.

    Unlike the original hybrid_search(), this version does NOT
    run the existing semantic-oriented reranker after fusion.

    Experiment hypothesis:

    The current reranker may be undoing useful BM25/RRF signals.
    """

    validate_hybrid_query(
        query=query,
        semantic_k=semantic_k,
        keyword_k=keyword_k,
        final_k=final_k,
        rrf_k=rrf_k,
    )

    semantic_results = semantic_search(
        query=query,
        embedded_chunks=embedded_chunks,
        model=model,
        embedding_model=embedding_model,
        candidate_k=semantic_k,
        final_k=semantic_k,
        min_similarity=semantic_min_similarity,
    )

    keyword_results = keyword_search(
        query=query,
        chunks=chunks,
        top_k=keyword_k,
        min_score=keyword_min_score,
    )

    fused_results = fuse_ranked_results(
        semantic_results=semantic_results,
        keyword_results=keyword_results,
        rrf_k=rrf_k,
    )

    return select_hybrid_results(
        fused_results=fused_results,
        final_k=final_k,
        min_rrf_score=min_rrf_score,
    )
