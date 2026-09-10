from __future__ import annotations


def rerank_candidates(
    candidates: list[dict],
) -> list[dict]:
    """
    Apply a deterministic second-stage reranking baseline.

    Current priorities:

    1. Active lifecycle status
    2. semantic similarity score
    3. deterministic chunk ID tie-break

    This is deliberately a transparent baseline rather
    than a learned AI reranking model.
    """

    if not isinstance(
        candidates,
        list,
    ):
        raise TypeError(
            "candidates must be a list"
        )

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
