from __future__ import annotations


def reciprocal_rank(
    retrieved_ids: list[str],
    expected_id: str,
) -> float:
    """
    Return reciprocal rank for the expected result.

    Example:
    expected result at rank 1 -> 1.0
    expected result at rank 2 -> 0.5
    expected result at rank 3 -> 0.333...
    not retrieved -> 0.0
    """

    for rank, chunk_id in enumerate(
        retrieved_ids,
        start=1,
    ):
        if chunk_id == expected_id:
            return 1.0 / rank

    return 0.0


def top_k_success(
    retrieved_ids: list[str],
    expected_id: str,
    k: int,
) -> bool:
    """
    Return True when the expected result appears
    within the first k retrieved results.
    """

    if (
        not isinstance(k, int)
        or isinstance(k, bool)
        or k <= 0
    ):
        raise ValueError(
            "k must be a positive integer"
        )

    return expected_id in retrieved_ids[:k]


def document_success(
    results: list[dict],
    expected_document_id: str,
    k: int,
) -> bool:
    """
    Return True when the expected document appears
    within the first k results.
    """

    if (
        not isinstance(k, int)
        or isinstance(k, bool)
        or k <= 0
    ):
        raise ValueError(
            "k must be a positive integer"
        )

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
    Return True when the expected document and page
    appear within the first k results.
    """

    if (
        not isinstance(k, int)
        or isinstance(k, bool)
        or k <= 0
    ):
        raise ValueError(
            "k must be a positive integer"
        )

    return any(
        result.get("document_id")
        == expected_document_id
        and result.get("page")
        == expected_page
        for result in results[:k]
    )


def active_only_success(
    results: list[dict],
) -> bool:
    """
    Confirm that every returned result belongs to
    an Active document.
    """

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
    Build QA metrics for one retrieval evaluation query.
    """

    retrieved_ids = [
        result.get("chunk_id")
        for result in results
        if result.get("chunk_id")
    ]

    report = {
        "query_id": query_id,
        "result_count": len(results),
        "active_only": active_only_success(
            results
        ),
    }

    if expected_chunk_id is not None:
        report["top_1_chunk_success"] = (
            top_k_success(
                retrieved_ids,
                expected_chunk_id,
                1,
            )
        )

        report["top_3_chunk_success"] = (
            top_k_success(
                retrieved_ids,
                expected_chunk_id,
                3,
            )
        )

        report["reciprocal_rank"] = (
            reciprocal_rank(
                retrieved_ids,
                expected_chunk_id,
            )
        )

    if expected_document_id is not None:
        report["top_1_document_success"] = (
            document_success(
                results,
                expected_document_id,
                1,
            )
        )

        report["top_3_document_success"] = (
            document_success(
                results,
                expected_document_id,
                3,
            )
        )

    if (
        expected_document_id is not None
        and expected_page is not None
    ):
        report["top_3_page_success"] = (
            page_success(
                results,
                expected_document_id,
                expected_page,
                3,
            )
        )

    return report
