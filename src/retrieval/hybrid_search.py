from __future__ import annotations

from src.retrieval.semantic_search import (
    semantic_search,
)

from src.retrieval.keyword_search import (
    keyword_search,
)

from src.retrieval.reranker import (
    rerank_candidates,
)

from src.ingestion.chunk_metadata import (
    validate_chunk_metadata,
    is_chunk_retrieval_eligible,
)


DEFAULT_RRF_K = 60


def validate_hybrid_query(
    query: str,
    semantic_k: int,
    keyword_k: int,
    final_k: int,
    rrf_k: int,
) -> None:
    """
    Validate hybrid retrieval request parameters.
    """

    if (
        not isinstance(query, str)
        or not query.strip()
    ):
        raise ValueError(
            "query must be a non-empty string"
        )

    for name, value in (
        ("semantic_k", semantic_k),
        ("keyword_k", keyword_k),
        ("final_k", final_k),
        ("rrf_k", rrf_k),
    ):
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(
                f"{name} must be a positive integer"
            )


def reciprocal_rank_contribution(
    rank: int,
    rrf_k: int = DEFAULT_RRF_K,
) -> float:
    """
    Calculate one Reciprocal Rank Fusion contribution.
    """

    if (
        not isinstance(rank, int)
        or isinstance(rank, bool)
        or rank <= 0
    ):
        raise ValueError(
            "rank must be a positive integer"
        )

    if (
        not isinstance(rrf_k, int)
        or isinstance(rrf_k, bool)
        or rrf_k <= 0
    ):
        raise ValueError(
            "rrf_k must be a positive integer"
        )

    return 1.0 / (
        rrf_k + rank
    )


def build_result_key(
    result: dict,
) -> str:
    """
    Build a stable identifier for result fusion.

    chunk_id is used because hybrid retrieval operates
    at chunk level rather than document level.
    """

    chunk_id = result.get(
        "chunk_id"
    )

    if (
        not isinstance(chunk_id, str)
        or not chunk_id.strip()
    ):
        raise ValueError(
            "retrieval result must contain a valid chunk_id"
        )

    return chunk_id


def fuse_ranked_results(
    semantic_results: list[dict],
    keyword_results: list[dict],
    rrf_k: int = DEFAULT_RRF_K,
) -> list[dict]:
    """
    Combine semantic and BM25 rankings using
    Reciprocal Rank Fusion.

    Raw semantic and BM25 scores are preserved for
    inspection but are not directly added together.
    """

    if not isinstance(
        semantic_results,
        list,
    ):
        raise TypeError(
            "semantic_results must be a list"
        )

    if not isinstance(
        keyword_results,
        list,
    ):
        raise TypeError(
            "keyword_results must be a list"
        )

    fused = {}

    for rank, result in enumerate(
        semantic_results,
        start=1,
    ):
        key = build_result_key(
            result
        )

        contribution = (
            reciprocal_rank_contribution(
                rank=rank,
                rrf_k=rrf_k,
            )
        )

        fused[key] = {
            **result,
            "semantic_rank": rank,
            "keyword_rank": None,
            "semantic_rrf_contribution": (
                contribution
            ),
            "keyword_rrf_contribution": 0.0,
            "rrf_score": contribution,
        }

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):
        key = build_result_key(
            result
        )

        contribution = (
            reciprocal_rank_contribution(
                rank=rank,
                rrf_k=rrf_k,
            )
        )

        if key in fused:
            existing = fused[
                key
            ]

            existing[
                "keyword_rank"
            ] = rank

            existing[
                "keyword_score"
            ] = result.get(
                "keyword_score"
            )

            existing[
                "keyword_rrf_contribution"
            ] = contribution

            existing[
                "rrf_score"
            ] += contribution

        else:
            fused[key] = {
                **result,
                "semantic_rank": None,
                "keyword_rank": rank,
                "semantic_rrf_contribution": 0.0,
                "keyword_rrf_contribution": (
                    contribution
                ),
                "rrf_score": contribution,
            }

    ranked = sorted(
        fused.values(),
        key=lambda item: (
            item[
                "rrf_score"
            ],
            item.get(
                "chunk_id",
                "",
            ),
        ),
        reverse=True,
    )

    results = []

    for hybrid_rank, result in enumerate(
        ranked,
        start=1,
    ):
        results.append(
            {
                **result,
                "hybrid_rank": (
                    hybrid_rank
                ),
            }
        )

    return results


def filter_hybrid_eligible_results(
    results: list[dict],
) -> list[dict]:
    """
    Re-check lifecycle eligibility after fusion.

    This gives hybrid retrieval its own governance boundary.
    """

    eligible_results = []

    for result in results:
        validate_chunk_metadata(
            result
        )

        if is_chunk_retrieval_eligible(
            result
        ):
            eligible_results.append(
                result
            )

    return eligible_results


def select_hybrid_results(
    fused_results: list[dict],
    final_k: int,
    min_rrf_score: float | None = None,
) -> list[dict]:
    """
    Select the final hybrid evidence set.
    """

    if (
        not isinstance(final_k, int)
        or isinstance(final_k, bool)
        or final_k <= 0
    ):
        raise ValueError(
            "final_k must be a positive integer"
        )

    if min_rrf_score is not None:
        if (
            isinstance(
                min_rrf_score,
                bool,
            )
            or not isinstance(
                min_rrf_score,
                (int, float),
            )
        ):
            raise TypeError(
                "min_rrf_score must be numeric"
            )

    eligible_results = (
        filter_hybrid_eligible_results(
            fused_results
        )
    )

    results = []

    for result in eligible_results:
        score = result[
            "rrf_score"
        ]

        if (
            min_rrf_score is not None
            and score < min_rrf_score
        ):
            continue

        results.append(
            {
                **result,
                "rank": len(results) + 1,
            }
        )

        if len(results) >= final_k:
            break

    return results


def hybrid_search(
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
    Perform governed hybrid retrieval.

    Flow:

    query
    -> semantic retrieval
    -> BM25 retrieval
    -> Reciprocal Rank Fusion
    -> lifecycle re-validation
    -> existing deterministic reranking
    -> optional RRF threshold
    -> final evidence
    """

    validate_hybrid_query(
        query=query,
        semantic_k=semantic_k,
        keyword_k=keyword_k,
        final_k=final_k,
        rrf_k=rrf_k,
    )

    semantic_results = (
        semantic_search(
            query=query,
            embedded_chunks=embedded_chunks,
            model=model,
            embedding_model=embedding_model,
            candidate_k=semantic_k,
            final_k=semantic_k,
            min_similarity=(
                semantic_min_similarity
            ),
        )
    )

    keyword_results = (
        keyword_search(
            query=query,
            chunks=chunks,
            top_k=keyword_k,
            min_score=keyword_min_score,
        )
    )

    fused_results = (
        fuse_ranked_results(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            rrf_k=rrf_k,
        )
    )

    eligible_results = (
        filter_hybrid_eligible_results(
            fused_results
        )
    )

    reranked_results = (
        rerank_candidates(
            eligible_results
        )
    )

    return select_hybrid_results(
        fused_results=reranked_results,
        final_k=final_k,
        min_rrf_score=min_rrf_score,
    )
