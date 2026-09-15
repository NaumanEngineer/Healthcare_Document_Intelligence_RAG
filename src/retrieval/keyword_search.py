from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from src.ingestion.chunk_metadata import (
    validate_chunk_metadata,
    is_chunk_retrieval_eligible,
)


def tokenise_text(
    text: str,
) -> list[str]:
    """
    Convert text into a simple lowercase token list.

    The tokenizer deliberately keeps the implementation
    transparent for learning and evaluation.
    """

    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    cleaned = text.lower()

    tokens = re.findall(
        r"\b[a-z0-9]+\b",
        cleaned,
    )

    return tokens


def validate_keyword_query(
    query: str,
    top_k: int,
) -> None:
    """
    Validate keyword retrieval request parameters.
    """

    if (
        not isinstance(query, str)
        or not query.strip()
    ):
        raise ValueError(
            "query must be a non-empty string"
        )

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or top_k <= 0
    ):
        raise ValueError(
            "top_k must be a positive integer"
        )


def filter_keyword_eligible_chunks(
    chunks: list[dict],
) -> list[dict]:
    """
    Apply the same lifecycle governance boundary used by
    semantic retrieval.

    Only retrieval-eligible chunks may enter BM25 search.
    """

    if not isinstance(
        chunks,
        list,
    ):
        raise TypeError(
            "chunks must be a list"
        )

    eligible_chunks = []

    for chunk in chunks:
        validate_chunk_metadata(
            chunk
        )

        if is_chunk_retrieval_eligible(
            chunk
        ):
            eligible_chunks.append(
                chunk
            )

    return eligible_chunks


def build_bm25_corpus(
    eligible_chunks: list[dict],
) -> list[list[str]]:
    """
    Tokenise eligible chunk text for BM25 indexing.
    """

    tokenised_corpus = []

    for chunk in eligible_chunks:
        text = chunk.get(
            "text"
        )

        if (
            not isinstance(text, str)
            or not text.strip()
        ):
            raise ValueError(
                "eligible chunk text must be non-empty"
            )

        tokenised_corpus.append(
            tokenise_text(
                text
            )
        )

    return tokenised_corpus


def score_keyword_chunks(
    query: str,
    eligible_chunks: list[dict],
) -> list[dict]:
    """
    Score eligible chunks using BM25.
    """

    if not eligible_chunks:
        return []

    tokenised_corpus = (
        build_bm25_corpus(
            eligible_chunks
        )
    )

    bm25 = BM25Okapi(
        tokenised_corpus
    )

    query_tokens = tokenise_text(
        query
    )

    scores = bm25.get_scores(
        query_tokens
    )

    scored_chunks = []

    for chunk, score in zip(
        eligible_chunks,
        scores,
    ):
        scored_chunks.append(
            {
                **chunk,
                "keyword_score": float(
                    score
                ),
            }
        )

    return scored_chunks


def rank_keyword_results(
    scored_chunks: list[dict],
    top_k: int,
    min_score: float | None = None,
) -> list[dict]:
    """
    Rank BM25 results and optionally reject weak matches.
    """

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or top_k <= 0
    ):
        raise ValueError(
            "top_k must be a positive integer"
        )

    if min_score is not None:
        if isinstance(
            min_score,
            bool,
        ) or not isinstance(
            min_score,
            (int, float),
        ):
            raise TypeError(
                "min_score must be numeric"
            )

    ranked = sorted(
        scored_chunks,
        key=lambda item: item[
            "keyword_score"
        ],
        reverse=True,
    )

    results = []

    for chunk in ranked:
        score = chunk[
            "keyword_score"
        ]

        if (
            min_score is not None
            and score < min_score
        ):
            continue

        results.append(
            {
                **chunk,
                "keyword_rank": (
                    len(results) + 1
                ),
            }
        )

        if len(results) >= top_k:
            break

    return results


def keyword_search(
    query: str,
    chunks: list[dict],
    top_k: int = 3,
    min_score: float | None = None,
) -> list[dict]:
    """
    Perform governed BM25 keyword retrieval.

    Flow:

    query
    -> validation
    -> lifecycle eligibility
    -> tokenisation
    -> BM25 scoring
    -> ranking
    -> optional score threshold
    -> final evidence
    """

    validate_keyword_query(
        query=query,
        top_k=top_k,
    )

    eligible_chunks = (
        filter_keyword_eligible_chunks(
            chunks
        )
    )

    if not eligible_chunks:
        return []

    scored_chunks = score_keyword_chunks(
        query=query,
        eligible_chunks=eligible_chunks,
    )

    return rank_keyword_results(
        scored_chunks=scored_chunks,
        top_k=top_k,
        min_score=min_score,
    )
