from __future__ import annotations

import math

from src.ingestion.chunk_metadata import (
    validate_chunk_metadata,
    is_chunk_retrieval_eligible,
)

from src.retrieval.embeddings import (
    embed_text,
    validate_vector,
    validate_embedding_dimensions,
    create_text_hash,
)

from src.retrieval.reranker import (
    rerank_candidates,
)


def validate_query(
    query: str,
    candidate_k: int,
    final_k: int,
    min_similarity: float | None = None,
) -> None:
    """
    Validate semantic retrieval request parameters.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError(
            "query must be a non-empty string"
        )

    if (
        not isinstance(candidate_k, int)
        or isinstance(candidate_k, bool)
        or candidate_k <= 0
    ):
        raise ValueError(
            "candidate_k must be a positive integer"
        )

    if (
        not isinstance(final_k, int)
        or isinstance(final_k, bool)
        or final_k <= 0
    ):
        raise ValueError(
            "final_k must be a positive integer"
        )

    if final_k > candidate_k:
        raise ValueError(
            "final_k must be less than or equal to candidate_k"
        )

    if min_similarity is not None:
        if isinstance(min_similarity, bool):
            raise TypeError(
                "min_similarity must be numeric"
            )

        if not isinstance(
            min_similarity,
            (int, float),
        ):
            raise TypeError(
                "min_similarity must be numeric"
            )

        if not math.isfinite(
            float(min_similarity)
        ):
            raise ValueError(
                "min_similarity must be finite"
            )

        if not -1.0 <= float(min_similarity) <= 1.0:
            raise ValueError(
                "min_similarity must be between -1.0 and 1.0"
            )


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Compute cosine similarity between two valid vectors.
    """

    validate_vector(vector_a)
    validate_vector(vector_b)

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have matching dimensions"
        )

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    norm_a = math.sqrt(
        sum(
            value ** 2
            for value in vector_a
        )
    )

    norm_b = math.sqrt(
        sum(
            value ** 2
            for value in vector_b
        )
    )

    return dot_product / (
        norm_a * norm_b
    )


def validate_embedding_freshness(
    chunk: dict,
) -> None:
    """
    Confirm that the stored embedding still represents
    the current chunk text.

    If the text has changed after embedding, the stored
    text_hash will no longer match.
    """

    chunk_id = chunk.get(
        "chunk_id",
        "<missing_chunk_id>",
    )

    text = chunk.get("text")
    stored_hash = chunk.get(
        "text_hash"
    )

    if not isinstance(
        stored_hash,
        str,
    ) or not stored_hash.strip():
        raise ValueError(
            "Missing text_hash for "
            f"chunk '{chunk_id}'"
        )

    current_hash = create_text_hash(
        text
    )

    if current_hash != stored_hash:
        raise ValueError(
            "Stale embedding detected for "
            f"chunk '{chunk_id}'"
        )


def filter_eligible_chunks(
    embedded_chunks: list[dict],
) -> list[dict]:
    """
    Keep only chunks satisfying canonical metadata
    validation and lifecycle retrieval eligibility.
    """

    eligible_chunks = []

    for chunk in embedded_chunks:
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


def validate_embedding_compatibility(
    embedded_chunks: list[dict],
    query_vector: list[float],
    embedding_model: str,
) -> None:
    """
    Confirm that query and document embeddings
    are technically compatible.
    """

    validate_vector(
        query_vector
    )

    if (
        not isinstance(
            embedding_model,
            str,
        )
        or not embedding_model.strip()
    ):
        raise ValueError(
            "embedding_model must be a non-empty string"
        )

    query_dimensions = len(
        query_vector
    )

    for chunk in embedded_chunks:
        chunk_id = chunk.get(
            "chunk_id",
            "<missing_chunk_id>",
        )

        chunk_model = chunk.get(
            "embedding_model"
        )

        chunk_dimensions = chunk.get(
            "embedding_dimensions"
        )

        vector = chunk.get(
            "vector"
        )

        if chunk_model != embedding_model:
            raise ValueError(
                "Embedding model mismatch for "
                f"chunk '{chunk_id}'"
            )

        if (
            not isinstance(
                chunk_dimensions,
                int,
            )
            or isinstance(
                chunk_dimensions,
                bool,
            )
            or chunk_dimensions <= 0
        ):
            raise ValueError(
                "Missing or invalid embedding_dimensions "
                f"for chunk '{chunk_id}'"
            )

        validate_vector(
            vector
        )

        validate_embedding_dimensions(
            vector,
            expected_dimensions=chunk_dimensions,
        )

        if chunk_dimensions != query_dimensions:
            raise ValueError(
                "Query and chunk embedding dimensions "
                f"do not match for chunk '{chunk_id}'"
            )


def validate_embedding_freshness_batch(
    embedded_chunks: list[dict],
) -> None:
    """
    Validate text-hash freshness for all candidate chunks.
    """

    for chunk in embedded_chunks:
        validate_embedding_freshness(
            chunk
        )


def score_chunks(
    eligible_chunks: list[dict],
    query_vector: list[float],
) -> list[dict]:
    """
    Add semantic similarity score to each eligible chunk.
    """

    scored_chunks = []

    for chunk in eligible_chunks:
        similarity_score = cosine_similarity(
            query_vector,
            chunk["vector"],
        )

        scored_chunks.append(
            {
                **chunk,
                "similarity_score": similarity_score,
            }
        )

    return scored_chunks


def rank_candidates(
    scored_chunks: list[dict],
    candidate_k: int,
) -> list[dict]:
    """
    Select the strongest initial semantic candidates.
    """

    if (
        not isinstance(candidate_k, int)
        or isinstance(candidate_k, bool)
        or candidate_k <= 0
    ):
        raise ValueError(
            "candidate_k must be a positive integer"
        )

    ranked_chunks = sorted(
        scored_chunks,
        key=lambda item: item[
            "similarity_score"
        ],
        reverse=True,
    )

    candidates = ranked_chunks[
        :candidate_k
    ]

    ranked_candidates = []

    for candidate_rank, chunk in enumerate(
        candidates,
        start=1,
    ):
        ranked_candidates.append(
            {
                **chunk,
                "candidate_rank": candidate_rank,
            }
        )

    return ranked_candidates


def select_final_results(
    candidates: list[dict],
    final_k: int,
    min_similarity: float | None = None,
) -> list[dict]:
    """
    Select final evidence.

    Weak evidence can be excluded using min_similarity.

    No universal similarity threshold is assumed.
    Threshold selection must be informed by evaluation.
    """

    if (
        not isinstance(final_k, int)
        or isinstance(final_k, bool)
        or final_k <= 0
    ):
        raise ValueError(
            "final_k must be a positive integer"
        )

    results = []

    for chunk in candidates:
        validate_chunk_metadata(
            chunk
        )

        if not is_chunk_retrieval_eligible(
            chunk
        ):
            continue

        similarity_score = chunk.get(
            "similarity_score"
        )

        if (
            min_similarity is not None
            and similarity_score < min_similarity
        ):
            continue

        results.append(
            {
                **chunk,
                "rank": len(results) + 1,
            }
        )

        if len(results) >= final_k:
            break

    return results


def semantic_search(
    query: str,
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    candidate_k: int = 10,
    final_k: int = 3,
    min_similarity: float | None = None,
) -> list[dict]:
    """
    Perform governed semantic retrieval.

    Flow:

    query
    -> validation
    -> lifecycle eligibility
    -> query embedding
    -> embedding compatibility
    -> stale-embedding detection
    -> cosine similarity
    -> candidate ranking
    -> deterministic reranking
    -> similarity threshold
    -> final evidence

    Returning [] represents insufficient or unavailable
    evidence rather than forcing an unrelated result.
    """

    validate_query(
        query=query,
        candidate_k=candidate_k,
        final_k=final_k,
        min_similarity=min_similarity,
    )

    eligible_chunks = filter_eligible_chunks(
        embedded_chunks
    )

    if not eligible_chunks:
        return []

    query_vector = embed_text(
        text=query,
        model=model,
    )

    validate_embedding_compatibility(
        embedded_chunks=eligible_chunks,
        query_vector=query_vector,
        embedding_model=embedding_model,
    )

    validate_embedding_freshness_batch(
        eligible_chunks
    )

    scored_chunks = score_chunks(
        eligible_chunks=eligible_chunks,
        query_vector=query_vector,
    )

    candidates = rank_candidates(
        scored_chunks=scored_chunks,
        candidate_k=candidate_k,
    )

    reranked_candidates = rerank_candidates(
        candidates
    )

    final_results = select_final_results(
        candidates=reranked_candidates,
        final_k=final_k,
        min_similarity=min_similarity,
    )

    return final_results
