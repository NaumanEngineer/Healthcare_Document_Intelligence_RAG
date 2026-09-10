from __future__ import annotations


def reciprocal_rank(
    retrieved_ids: list[str],
    expected_id: str,
) -> float:
    """
    Return reciprocal rank for an expected result.

    Rank 1 -> 1.0
    Rank 2 -> 0.5
    Rank 3 -> 0.333...
    Missing -> 0.0
    """

    for rank, chunk_id in enumerate(
        retrieved_ids,
        start=1,
    ):
        if chunk_id == expected_id:
            return 1.0 / rank

    return 0.0


def validate_k(
    k: int,
) -> None:
    """
    Validate a top-k evaluation parameter.
    """

    if (
        not isinstance(k, int)
        or isinstance(k, bool)
        or k <= 0
    ):
        raise ValueError(
            "k must be a positive integer"
        )


def top_k_success(
    retrieved_ids: list[str],
    expected_id: str,
    k: int,
) -> bool:
    """
    Return True when the expected chunk appears
    inside the first k results.
    """

    validate_k(k)

    return expected_id in (
        retrieved_ids[:k]
    )


def document_success(
    results: list[dict],
    expected_document_id: str,
    k: int,
) -> bool:
    """
    Return True when the expected document appears
    inside the first k retrieval results.
    """

    validate_k(k)

    return any(
        result.get("document_id")
        == expected_document_id
        for result in results[:k]
    )


def page_success(
    results: list[dict],
    expected_document_id: str,
    expected_page: int,
    k: int,
) -> bool:
    """
    Return True when the expected document/page
    combination appears inside the first k results.
    """

    validate_k(k)

    return any(
        result.get("document_id")
        == expected_document_id
        and result.get("page")
        == expected_page
        for result in results[:k]
    )


def active_only_success(
    results: list[dict],
) -> bool | None:
    """
    Confirm all returned evidence belongs to Active documents.

    None means no evidence was returned.
    """

    if not results:
        return None

    return all(
        result.get("status") == "Active"
        for result in results
    )


def build_retrieval_qa_result(
    query_id: str,
    results: list[dict],
    expected_chunk_id: str | None = None,
    expected_document_id: str | None = None,
    expected_page: int | None = None,
) -> dict:
    """
    Build retrieval QA metrics for one evaluation query.
    """

    if (
        not isinstance(query_id, str)
        or not query_id.strip()
    ):
        raise ValueError(
            "query_id must be a non-empty string"
        )

    retrieved_ids = [
        result.get("chunk_id")
        for result in results
        if result.get("chunk_id")
    ]

    report = {
        "query_id": query_id,
        "result_count": len(results),
        "no_results": len(results) == 0,
        "active_only": active_only_success(
            results
        ),
    }

    if expected_chunk_id is not None:
        report[
            "top_1_chunk_success"
        ] = top_k_success(
            retrieved_ids,
            expected_chunk_id,
            1,
        )

        report[
            "top_3_chunk_success"
        ] = top_k_success(
            retrieved_ids,
            expected_chunk_id,
            3,
        )

        report[
            "reciprocal_rank"
        ] = reciprocal_rank(
            retrieved_ids,
            expected_chunk_id,
        )

    if expected_document_id is not None:
        report[
            "top_1_document_success"
        ] = document_success(
            results,
            expected_document_id,
            1,
        )

        report[
            "top_3_document_success"
        ] = document_success(
            results,
            expected_document_id,
            3,
        )

    if (
        expected_document_id is not None
        and expected_page is not None
    ):
        report[
            "top_3_page_success"
        ] = page_success(
            results,
            expected_document_id,
            expected_page,
            3,
        )

    return report
