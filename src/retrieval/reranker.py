from __future__ import annotations


def rerank_candidates(
    candidates: list[dict],
) -> list[dict]:
    """
    Apply a lightweight deterministic reranking policy.

    Current prototype priorities:
    1. Active lifecycle status
    2. higher semantic similarity
    3. deterministic chunk ID tie-break

    More advanced reranking models are intentionally deferred.
    """

    reranked = sorted(
        candidates,
        key=lambda item: (
            item.get("status") == "Active",
            item.get(
                "similarity_score",
                float("-inf"),
            ),
            item.get(
                "chunk_id",
                "",
            ),
        ),
        reverse=True,
    )

    results = []

    for rank, candidate in enumerate(
        reranked,
        start=1,
    ):
        results.append(
            {
                **candidate,
                "rerank_rank": rank,
            }
        )

    return results
