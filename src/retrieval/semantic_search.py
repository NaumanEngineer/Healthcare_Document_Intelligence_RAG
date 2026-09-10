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
)


def validate_query(
    query: str,
    candidate_k: int,
    final_k: int,
) -> None:
    """
    Validate retrieval request parameters.
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


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Compute cosine similarity between two embedding vectors.
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


def filter_eligible_chunks(
    embedded_chunks: list[dict],
) -> list[dict]:
    """
    Keep only chunks that pass canonical metadata validation
    and satisfy retrieval eligibility.
    """

    eligible_chunks = []

    for chunk in embedded_chunks:
        validate_chunk_metadata(chunk)

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
    Validate that query and chunk embeddings are compatible.
    """

    validate_vector(
        query_vector
    )

    if (
        not isinstance(embedding_model, str)
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


def score_chunks(
    eligible_chunks: list[dict],
    query_vector: list[float],
) -> list[dict]:
    """
    Calculate semantic similarity scores for eligible chunks.
    """

    scored_chunks = []

    for chunk in eligible_chunks:
        similarity_score = (
            cosine_similarity(
                query_vector,
                chunk["vector"],
            )
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
    Return the highest-scoring semantic candidates.
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
) -> list[dict]:
    """
    Return final retrieval evidence.

    Reranking is not yet implemented, so semantic candidate
    order is preserved.
    """

    if (
        not isinstance(final_k, int)
        or isinstance(final_k, bool)
        or final_k <= 0
    ):
        raise ValueError(
            "final_k must be a positive integer"
        )

    final_candidates = (
        candidates[:final_k]
    )

    results = []

    for rank, chunk in enumerate(
        final_candidates,
        start=1,
    ):
        validate_chunk_metadata(
            chunk
        )

        if not is_chunk_retrieval_eligible(
            chunk
        ):
            continue

        results.append(
            {
                **chunk,
                "rank": rank,
            }
        )

    return results


def semantic_search(
    query: str,
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    candidate_k: int = 10,
    final_k: int = 3,
) -> list[dict]:
    """
    Perform governed semantic retrieval.

    Flow:
    1. validate query
    2. filter to eligible chunks
    3. embed query
    4. validate embedding compatibility
    5. score eligible chunks
    6. rank semantic candidates
    7. select final evidence

    Returns an empty list when no eligible evidence exists.
    """

    validate_query(
        query=query,
        candidate_k=candidate_k,
        final_k=final_k,
    )

    eligible_chunks = (
        filter_eligible_chunks(
            embedded_chunks
        )
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

    scored_chunks = score_chunks(
        eligible_chunks=eligible_chunks,
        query_vector=query_vector,
    )

    candidates = rank_candidates(
        scored_chunks=scored_chunks,
        candidate_k=candidate_k,
    )

    final_results = select_final_results(
        candidates=candidates,
        final_k=final_k,
    )

    return final_results
