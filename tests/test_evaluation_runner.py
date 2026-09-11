from src.evaluation.evaluation_runner import (
    expected_document_ids,
    evaluate_expected_documents,
    evaluate_abstention,
    summarise_retrieval_evaluation,
)


def build_case() -> dict:
    return {
        "query_id": "Q001",
        "category": "escalation",
        "question": (
            "What should operational leadership do?"
        ),
        "expected_document_id": (
            "DOC-001"
        ),
        "expected_answerable": True,
        "expected_abstention": False,
    }


def build_result(
    document_id: str,
) -> dict:
    return {
        "document_id": (
            document_id
        ),
        "chunk_id": (
            f"{document_id}-V1.0-P001-C001"
        ),
        "status": "Active",
        "similarity_score": 0.9,
    }


def test_expected_document_ids_single():
    case = build_case()

    result = expected_document_ids(
        case
    )

    assert result == [
        "DOC-001"
    ]


def test_expected_document_ids_multiple():
    case = build_case()

    case[
        "expected_document_id"
    ] = None

    case[
        "expected_document_ids"
    ] = [
        "DOC-003",
        "DOC-004",
    ]

    result = expected_document_ids(
        case
    )

    assert result == [
        "DOC-003",
        "DOC-004",
    ]


def test_expected_documents_found():
    results = [
        build_result(
            "DOC-001"
        ),
        build_result(
            "DOC-002"
        ),
    ]

    qa = (
        evaluate_expected_documents(
            results=results,
            expected_ids=[
                "DOC-001"
            ],
            k=3,
        )
    )

    assert (
        qa[
            "all_expected_documents_found"
        ]
        is True
    )


def test_cross_document_success():
    results = [
        build_result(
            "DOC-003"
        ),
        build_result(
            "DOC-004"
        ),
    ]

    qa = (
        evaluate_expected_documents(
            results=results,
            expected_ids=[
                "DOC-003",
                "DOC-004",
            ],
            k=3,
        )
    )

    assert (
        qa[
            "expected_documents_found"
        ]
        == 2
    )

    assert (
        qa[
            "all_expected_documents_found"
        ]
        is True
    )


def test_expected_document_failure():
    results = [
        build_result(
            "DOC-999"
        )
    ]

    qa = (
        evaluate_expected_documents(
            results=results,
            expected_ids=[
                "DOC-001"
            ],
            k=3,
        )
    )

    assert (
        qa[
            "all_expected_documents_found"
        ]
        is False
    )


def test_abstention_success_when_no_results():
    case = build_case()

    case[
        "expected_answerable"
    ] = False

    case[
        "expected_abstention"
    ] = True

    qa = evaluate_abstention(
        case=case,
        results=[],
    )

    assert (
        qa[
            "abstention_correct"
        ]
        is True
    )


def test_answerable_case_requires_results():
    case = build_case()

    qa = evaluate_abstention(
        case=case,
        results=[
            build_result(
                "DOC-001"
            )
        ],
    )

    assert (
        qa[
            "abstention_correct"
        ]
        is True
    )


def test_summary_metrics():
    evaluation_results = [
        {
            "retrieval_qa": {
                "active_only": True,
            },
            "document_qa": {
                "all_expected_documents_found": True,
            },
            "abstention_qa": {
                "abstention_correct": True,
            },
        },
        {
            "retrieval_qa": {
                "active_only": True,
            },
            "document_qa": {
                "all_expected_documents_found": False,
            },
            "abstention_qa": {
                "abstention_correct": True,
            },
        },
    ]

    summary = (
        summarise_retrieval_evaluation(
            evaluation_results
        )
    )

    assert (
        summary[
            "queries_evaluated"
        ]
        == 2
    )

    assert (
        summary[
            "abstention_accuracy"
        ]
        == 1.0
    )

    assert (
        summary[
            "document_success_rate"
        ]
        == 0.5
    )

    assert (
        summary[
            "active_only_compliance_rate"
        ]
        == 1.0
    )
