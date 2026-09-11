from __future__ import annotations

from src.evaluation.retrieval_qa import (
    build_retrieval_qa_result,
)

from src.retrieval.semantic_search import (
    semantic_search,
)


def validate_evaluation_inputs(
    cases: list[dict],
    embedded_chunks: list[dict],
) -> None:
    """
    Validate the main inputs used by the evaluation runner.
    """

    if not isinstance(cases, list):
        raise TypeError(
            "cases must be a list"
        )

    if not cases:
        raise ValueError(
            "cases must not be empty"
        )

    if not isinstance(
        embedded_chunks,
        list,
    ):
        raise TypeError(
            "embedded_chunks must be a list"
        )


def expected_document_ids(
    case: dict,
) -> list[str]:
    """
    Return all expected document IDs for an evaluation case.

    Supports both:

    expected_document_id

    and:

    expected_document_ids
    """

    expected = []

    single_id = case.get(
        "expected_document_id"
    )

    if (
        isinstance(single_id, str)
        and single_id.strip()
    ):
        expected.append(
            single_id
        )

    multiple_ids = case.get(
        "expected_document_ids",
        [],
    )

    if isinstance(
        multiple_ids,
        list,
    ):
        for document_id in multiple_ids:
            if (
                isinstance(
                    document_id,
                    str,
                )
                and document_id.strip()
                and document_id not in expected
            ):
                expected.append(
                    document_id
                )

    return expected


def evaluate_expected_documents(
    results: list[dict],
    expected_ids: list[str],
    k: int = 3,
) -> dict:
    """
    Evaluate expected-document retrieval.

    For a single-document case, success means that document
    appears within top-k.

    For a cross-document case, all expected documents must
    appear within top-k.
    """

    retrieved_ids = [
        result.get(
            "document_id"
        )
        for result in results[:k]
    ]

    if not expected_ids:
        return {
            "expected_document_count": 0,
            "expected_documents_found": 0,
            "all_expected_documents_found": None,
        }

    found_count = sum(
        1
        for document_id in expected_ids
        if document_id in retrieved_ids
    )

    return {
        "expected_document_count": len(
            expected_ids
        ),
        "expected_documents_found": found_count,
        "all_expected_documents_found": (
            found_count
            == len(expected_ids)
        ),
    }


def evaluate_abstention(
    case: dict,
    results: list[dict],
) -> dict:
    """
    Evaluate whether retrieval behaviour matches the
    benchmark's expected abstention behaviour.
    """

    expected_abstention = case[
        "expected_abstention"
    ]

    no_results = len(results) == 0

    if expected_abstention:
        correct = no_results
    else:
        correct = not no_results

    return {
        "expected_abstention": (
            expected_abstention
        ),
        "retrieval_returned_no_evidence": (
            no_results
        ),
        "abstention_correct": correct,
    }


def evaluate_single_case(
    case: dict,
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    candidate_k: int = 10,
    final_k: int = 3,
    min_similarity: float | None = None,
) -> dict:
    """
    Run semantic retrieval for one benchmark question
    and calculate retrieval evaluation metrics.
    """

    results = semantic_search(
        query=case["question"],
        embedded_chunks=embedded_chunks,
        model=model,
        embedding_model=embedding_model,
        candidate_k=candidate_k,
        final_k=final_k,
        min_similarity=min_similarity,
    )

    expected_ids = (
        expected_document_ids(
            case
        )
    )

    expected_document_id = (
        case.get(
            "expected_document_id"
        )
    )

    expected_chunk_id = (
        case.get(
            "expected_chunk_id"
        )
    )

    expected_page = (
        case.get(
            "expected_page"
        )
    )

    retrieval_qa = (
        build_retrieval_qa_result(
            query_id=case[
                "query_id"
            ],
            results=results,
            expected_chunk_id=expected_chunk_id,
            expected_document_id=expected_document_id,
            expected_page=expected_page,
        )
    )

    document_qa = (
        evaluate_expected_documents(
            results=results,
            expected_ids=expected_ids,
            k=final_k,
        )
    )

    abstention_qa = (
        evaluate_abstention(
            case=case,
            results=results,
        )
    )

    return {
        "query_id": case[
            "query_id"
        ],
        "category": case[
            "category"
        ],
        "question": case[
            "question"
        ],
        "expected_answerable": case[
            "expected_answerable"
        ],
        "retrieved_document_ids": [
            result.get(
                "document_id"
            )
            for result in results
        ],
        "retrieved_chunk_ids": [
            result.get(
                "chunk_id"
            )
            for result in results
        ],
        "retrieved_similarity_scores": [
            result.get(
                "similarity_score"
            )
            for result in results
        ],
        "retrieval_qa": retrieval_qa,
        "document_qa": document_qa,
        "abstention_qa": abstention_qa,
    }


def run_retrieval_evaluation(
    cases: list[dict],
    embedded_chunks: list[dict],
    model,
    embedding_model: str,
    candidate_k: int = 10,
    final_k: int = 3,
    min_similarity: float | None = None,
) -> list[dict]:
    """
    Run all benchmark cases through governed semantic retrieval.
    """

    validate_evaluation_inputs(
        cases,
        embedded_chunks,
    )

    results = []

    for case in cases:
        evaluation_result = (
            evaluate_single_case(
                case=case,
                embedded_chunks=embedded_chunks,
                model=model,
                embedding_model=embedding_model,
                candidate_k=candidate_k,
                final_k=final_k,
                min_similarity=min_similarity,
            )
        )

        results.append(
            evaluation_result
        )

    return results


def summarise_retrieval_evaluation(
    evaluation_results: list[dict],
) -> dict:
    """
    Produce high-level retrieval evaluation metrics.
    """

    if not isinstance(
        evaluation_results,
        list,
    ):
        raise TypeError(
            "evaluation_results must be a list"
        )

    if not evaluation_results:
        raise ValueError(
            "evaluation_results must not be empty"
        )

    total_queries = len(
        evaluation_results
    )

    abstention_correct = sum(
        1
        for result in evaluation_results
        if result[
            "abstention_qa"
        ][
            "abstention_correct"
        ]
    )

    document_cases = [
        result
        for result in evaluation_results
        if result[
            "document_qa"
        ][
            "all_expected_documents_found"
        ]
        is not None
    ]

    document_successes = sum(
        1
        for result in document_cases
        if result[
            "document_qa"
        ][
            "all_expected_documents_found"
        ]
    )

    active_compliance_cases = [
        result[
            "retrieval_qa"
        ][
            "active_only"
        ]
        for result in evaluation_results
        if result[
            "retrieval_qa"
        ][
            "active_only"
        ]
        is not None
    ]

    active_compliance_successes = sum(
        1
        for value in active_compliance_cases
        if value is True
    )

    return {
        "queries_evaluated": (
            total_queries
        ),
        "abstention_accuracy": (
            abstention_correct
            / total_queries
        ),
        "document_cases_evaluated": (
            len(document_cases)
        ),
        "document_success_rate": (
            document_successes
            / len(document_cases)
            if document_cases
            else None
        ),
        "active_only_cases_evaluated": (
            len(
                active_compliance_cases
            )
        ),
        "active_only_compliance_rate": (
            active_compliance_successes
            / len(
                active_compliance_cases
            )
            if active_compliance_cases
            else None
        ),
    }
