from __future__ import annotations


def get_expected_document_ids(
    case: dict,
) -> list[str]:
    """
    Return expected document IDs in a consistent list form.

    Supports either:
    - expected_document_id
    - expected_document_ids
    """

    multiple = case.get(
        "expected_document_ids"
    )

    if multiple is not None:
        if not isinstance(
            multiple,
            list,
        ):
            raise TypeError(
                "expected_document_ids must be a list"
            )

        return [
            document_id
            for document_id in multiple
            if isinstance(document_id, str)
            and document_id.strip()
        ]

    single = case.get(
        "expected_document_id"
    )

    if (
        isinstance(single, str)
        and single.strip()
    ):
        return [
            single
        ]

    return []


def get_result_document_ids(
    results: list[dict],
    top_k: int = 3,
) -> list[str]:
    """
    Return unique document IDs from the first top_k results.
    """

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or top_k <= 0
    ):
        raise ValueError(
            "top_k must be a positive integer"
        )

    document_ids = []

    for result in results[:top_k]:
        document_id = result.get(
            "document_id"
        )

        if (
            isinstance(document_id, str)
            and document_id not in document_ids
        ):
            document_ids.append(
                document_id
            )

    return document_ids


def active_only_success(
    results: list[dict],
) -> bool:
    """
    Confirm all returned evidence is Active.

    Empty results are considered compliant because no
    ineligible evidence was returned.
    """

    return all(
        result.get("status") == "Active"
        for result in results
    )


def evaluate_retrieval_results(
    case: dict,
    results: list[dict],
    top_k: int = 3,
) -> dict:
    """
    Evaluate one retrieval method against one benchmark case.
    """

    query_id = case.get(
        "query_id"
    )

    expected_ids = (
        get_expected_document_ids(
            case
        )
    )

    expected_abstention = bool(
        case.get(
            "expected_abstention",
            False,
        )
    )

    retrieved_ids = (
        get_result_document_ids(
            results=results,
            top_k=top_k,
        )
    )

    top_document = (
        retrieved_ids[0]
        if retrieved_ids
        else None
    )

    if expected_ids:
        top1_success = (
            top_document
            in expected_ids
        )

        topk_success = all(
            expected_id
            in retrieved_ids
            for expected_id in expected_ids
        )
    else:
        top1_success = None
        topk_success = None

    if expected_abstention:
        abstention_success = (
            len(results) == 0
        )
    else:
        abstention_success = None

    return {
        "query_id": query_id,
        "expected_document_ids": (
            expected_ids
        ),
        "retrieved_document_ids": (
            retrieved_ids
        ),
        "top1_success": (
            top1_success
        ),
        "topk_success": (
            topk_success
        ),
        "expected_abstention": (
            expected_abstention
        ),
        "abstention_success": (
            abstention_success
        ),
        "active_only_success": (
            active_only_success(
                results
            )
        ),
        "result_count": len(
            results
        ),
    }


def compare_methods_for_case(
    case: dict,
    semantic_results: list[dict],
    keyword_results: list[dict],
    hybrid_results: list[dict],
    top_k: int = 3,
) -> dict:
    """
    Compare semantic, keyword and hybrid retrieval
    for the same benchmark case.
    """

    return {
        "query_id": case.get(
            "query_id"
        ),
        "question": case.get(
            "question"
        ),
        "semantic": (
            evaluate_retrieval_results(
                case=case,
                results=semantic_results,
                top_k=top_k,
            )
        ),
        "keyword": (
            evaluate_retrieval_results(
                case=case,
                results=keyword_results,
                top_k=top_k,
            )
        ),
        "hybrid": (
            evaluate_retrieval_results(
                case=case,
                results=hybrid_results,
                top_k=top_k,
            )
        ),
    }


def _rate(
    numerator: int,
    denominator: int,
) -> float | None:
    if denominator == 0:
        return None

    return numerator / denominator


def summarise_method(
    case_results: list[dict],
    method_name: str,
) -> dict:
    """
    Summarise benchmark performance for one retrieval method.
    """

    top1_values = []
    topk_values = []
    abstention_values = []
    active_values = []

    for case_result in case_results:
        method = case_result[
            method_name
        ]

        if (
            method[
                "top1_success"
            ]
            is not None
        ):
            top1_values.append(
                method[
                    "top1_success"
                ]
            )

        if (
            method[
                "topk_success"
            ]
            is not None
        ):
            topk_values.append(
                method[
                    "topk_success"
                ]
            )

        if (
            method[
                "abstention_success"
            ]
            is not None
        ):
            abstention_values.append(
                method[
                    "abstention_success"
                ]
            )

        active_values.append(
            method[
                "active_only_success"
            ]
        )

    return {
        "top1_success_rate": _rate(
            sum(top1_values),
            len(top1_values),
        ),
        "topk_success_rate": _rate(
            sum(topk_values),
            len(topk_values),
        ),
        "abstention_success_rate": _rate(
            sum(abstention_values),
            len(abstention_values),
        ),
        "active_only_rate": _rate(
            sum(active_values),
            len(active_values),
        ),
        "evaluated_cases": len(
            case_results
        ),
    }


def summarise_benchmark(
    case_results: list[dict],
) -> dict:
    """
    Produce side-by-side benchmark summary.
    """

    return {
        "semantic": summarise_method(
            case_results,
            "semantic",
        ),
        "keyword": summarise_method(
            case_results,
            "keyword",
        ),
        "hybrid": summarise_method(
            case_results,
            "hybrid",
        ),
    }
