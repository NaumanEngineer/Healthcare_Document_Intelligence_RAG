from src.evaluation.retrieval_benchmark import (
    get_expected_document_ids,
    get_result_document_ids,
    active_only_success,
    evaluate_retrieval_results,
    compare_methods_for_case,
    summarise_benchmark,
)


def build_result(
    document_id: str,
    status: str = "Active",
) -> dict:
    return {
        "document_id": document_id,
        "status": status,
    }


def test_get_expected_single_document():
    case = {
        "expected_document_id": "DOC-008"
    }

    assert (
        get_expected_document_ids(
            case
        )
        == ["DOC-008"]
    )


def test_get_expected_multiple_documents():
    case = {
        "expected_document_ids": [
            "DOC-003",
            "DOC-004",
        ]
    }

    assert (
        get_expected_document_ids(
            case
        )
        == [
            "DOC-003",
            "DOC-004",
        ]
    )


def test_get_result_document_ids_removes_duplicates():
    results = [
        build_result("DOC-008"),
        build_result("DOC-008"),
        build_result("DOC-012"),
    ]

    assert (
        get_result_document_ids(
            results,
            top_k=3,
        )
        == [
            "DOC-008",
            "DOC-012",
        ]
    )


def test_active_only_success():
    results = [
        build_result(
            "DOC-008",
            status="Active",
        )
    ]

    assert (
        active_only_success(
            results
        )
        is True
    )


def test_active_only_detects_superseded():
    results = [
        build_result(
            "DOC-001",
            status="Superseded",
        )
    ]

    assert (
        active_only_success(
            results
        )
        is False
    )


def test_evaluate_top1_success():
    case = {
        "query_id": "Q001",
        "expected_document_id": "DOC-008",
        "expected_abstention": False,
    }

    results = [
        build_result("DOC-008"),
        build_result("DOC-012"),
    ]

    evaluation = (
        evaluate_retrieval_results(
            case=case,
            results=results,
        )
    )

    assert (
        evaluation[
            "top1_success"
        ]
        is True
    )


def test_cross_document_topk_success():
    case = {
        "query_id": "Q011",
        "expected_document_ids": [
            "DOC-003",
            "DOC-004",
        ],
        "expected_abstention": False,
    }

    results = [
        build_result("DOC-003"),
        build_result("DOC-004"),
    ]

    evaluation = (
        evaluate_retrieval_results(
            case=case,
            results=results,
        )
    )

    assert (
        evaluation[
            "topk_success"
        ]
        is True
    )


def test_abstention_success_when_no_results():
    case = {
        "query_id": "Q007",
        "expected_abstention": True,
    }

    evaluation = (
        evaluate_retrieval_results(
            case=case,
            results=[],
        )
    )

    assert (
        evaluation[
            "abstention_success"
        ]
        is True
    )


def test_compare_methods():
    case = {
        "query_id": "Q001",
        "question": "Test question",
        "expected_document_id": "DOC-008",
        "expected_abstention": False,
    }

    comparison = (
        compare_methods_for_case(
            case=case,
            semantic_results=[
                build_result(
                    "DOC-012"
                )
            ],
            keyword_results=[
                build_result(
                    "DOC-008"
                )
            ],
            hybrid_results=[
                build_result(
                    "DOC-008"
                )
            ],
        )
    )

    assert (
        comparison[
            "semantic"
        ][
            "top1_success"
        ]
        is False
    )

    assert (
        comparison[
            "keyword"
        ][
            "top1_success"
        ]
        is True
    )

    assert (
        comparison[
            "hybrid"
        ][
            "top1_success"
        ]
        is True
    )


def test_summarise_benchmark():
    case_results = [
        {
            "semantic": {
                "top1_success": True,
                "topk_success": True,
                "abstention_success": None,
                "active_only_success": True,
            },
            "keyword": {
                "top1_success": False,
                "topk_success": True,
                "abstention_success": None,
                "active_only_success": True,
            },
            "hybrid": {
                "top1_success": True,
                "topk_success": True,
                "abstention_success": None,
                "active_only_success": True,
            },
        }
    ]

    summary = summarise_benchmark(
        case_results
    )

    assert (
        summary[
            "semantic"
        ][
            "top1_success_rate"
        ]
        == 1.0
    )

    assert (
        summary[
            "keyword"
        ][
            "top1_success_rate"
        ]
        == 0.0
    )

    assert (
        summary[
            "hybrid"
        ][
            "top1_success_rate"
        ]
        == 1.0
    )
