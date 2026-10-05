from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from numbers import Real


RelevanceScorer = Callable[[list[tuple[str, str]]], Iterable[float]]


def rerank_relevance(
    query: str,
    candidates: list[dict],
    *,
    scorer: RelevanceScorer,
) -> list[dict]:
    """Score query/text pairs; return copies in descending relevance order.

    The callable returns one finite real score per pair, in input order.
    Equal scores preserve input order. No lifecycle decisions, thresholds or
    truncation occur here. Existing retrieval fields remain unchanged; the
    relevance_score/relevance_rank fields describe this invocation.
    Scorer failures propagate rather than silently falling back.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise TypeError("each candidate must be a dictionary")
        if not isinstance(candidate.get("text"), str) or not candidate["text"].strip():
            raise ValueError("candidate text must be a non-empty string")
    if not callable(scorer):
        raise TypeError("scorer must be callable")
    if not candidates:
        return []

    scores = list(scorer([(query, candidate["text"]) for candidate in candidates]))
    if len(scores) != len(candidates):
        raise ValueError("scorer must return one score per candidate")
    for score in scores:
        if isinstance(score, bool) or not isinstance(score, Real):
            raise TypeError("relevance scores must be real numbers")
        if not math.isfinite(score):
            raise ValueError("relevance scores must be finite")

    ranked = sorted(zip(candidates, scores), key=lambda item: item[1], reverse=True)
    return [
        {**candidate, "relevance_score": float(score), "relevance_rank": rank}
        for rank, (candidate, score) in enumerate(ranked, start=1)
    ]


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



def rerank_hybrid_candidates(
    candidates: list[dict],
) -> list[dict]:
    """Rank by Active status, descending RRF score, then descending chunk ID.

    Preserve fusion audit fields without reintroducing semantic-score bias.
    Return copies so the original candidates remain unchanged.
    """
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list")

    reranked = sorted(
        candidates,
        key=lambda item: (
            item.get("status") == "Active",
            item.get("rrf_score", float("-inf")),
            item.get("chunk_id", ""),
        ),
        reverse=True,
    )
    return [
        {**candidate, "hybrid_rerank_rank": rank}
        for rank, candidate in enumerate(reranked, start=1)
    ]
