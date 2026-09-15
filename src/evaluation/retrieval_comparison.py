from __future__ import annotations

from src.retrieval.keyword_search import (
    keyword_search,
)

from src.retrieval.semantic_search import (
    semantic_search,
)


def compare_query(
    query: str,
    chunks: list[dict],
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    top_k: int = 3,
    semantic_min_similarity: float | None = None,
    keyword_min_score: float | None = None,
) -> dict:
    """
    Compare semantic and keyword retrieval for one query.
    """

    semantic_results = semantic_search(
        query=query,
        embedded_chunks=embedded_chunks,
        model=model,
        embedding_model=embedding_model,
        candidate_k=max(
            top_k,
            10,
        ),
        final_k=top_k,
        min_similarity=semantic_min_similarity,
    )

    keyword_results = keyword_search(
        query=query,
        chunks=chunks,
        top_k=top_k,
        min_score=keyword_min_score,
    )

    return {
        "query": query,
        "semantic_results": [
            {
                "rank": result.get("rank"),
                "document_id": result.get(
                    "document_id"
                ),
                "title": result.get(
                    "title"
                ),
                "chunk_id": result.get(
                    "chunk_id"
                ),
                "similarity_score": result.get(
                    "similarity_score"
                ),
            }
            for result in semantic_results
        ],
        "keyword_results": [
            {
                "rank": result.get(
                    "keyword_rank"
                ),
                "document_id": result.get(
                    "document_id"
                ),
                "title": result.get(
                    "title"
                ),
                "chunk_id": result.get(
                    "chunk_id"
                ),
                "keyword_score": result.get(
                    "keyword_score"
                ),
            }
            for result in keyword_results
        ],
    }


def top_document_id(
    results: list[dict],
) -> str | None:
    """
    Return the document ID of the first result.
    """

    if not results:
        return None

    return results[0].get(
        "document_id"
    )


def compare_expected_document(
    comparison: dict,
    expected_document_id: str | None,
) -> dict:
    """
    Compare top-1 performance against an expected document.
    """

    semantic_top = top_document_id(
        comparison[
            "semantic_results"
        ]
    )

    keyword_top = top_document_id(
        comparison[
            "keyword_results"
        ]
    )

    return {
        "expected_document_id": expected_document_id,
        "semantic_top_document": semantic_top,
        "keyword_top_document": keyword_top,
        "semantic_top1_success": (
            semantic_top
            == expected_document_id
            if expected_document_id
            is not None
            else None
        ),
        "keyword_top1_success": (
            keyword_top
            == expected_document_id
            if expected_document_id
            is not None
            else None
        ),
    }
