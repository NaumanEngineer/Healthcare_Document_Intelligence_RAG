from src.evaluation.retrieval_comparison import (
    top_document_id,
    compare_expected_document,
)


def test_top_document_id_returns_first_document():
    results = [
        {
            "document_id": "DOC-008"
        },
        {
            "document_id": "DOC-001"
        },
    ]

    assert (
        top_document_id(results)
        == "DOC-008"
    )


def test_top_document_id_empty_returns_none():
    assert (
        top_document_id([])
        is None
    )


def test_compare_expected_document_both_success():
    comparison = {
        "semantic_results": [
            {
                "document_id": "DOC-008"
            }
        ],
        "keyword_results": [
            {
                "document_id": "DOC-008"
            }
        ],
    }

    result = compare_expected_document(
        comparison=comparison,
        expected_document_id="DOC-008",
    )

    assert (
        result[
            "semantic_top1_success"
        ]
        is True
    )

    assert (
        result[
            "keyword_top1_success"
        ]
        is True
    )


def test_compare_expected_document_can_show_different_winner():
    comparison = {
        "semantic_results": [
            {
                "document_id": "DOC-012"
            }
        ],
        "keyword_results": [
            {
                "document_id": "DOC-008"
            }
        ],
    }

    result = compare_expected_document(
        comparison=comparison,
        expected_document_id="DOC-008",
    )

    assert (
        result[
            "semantic_top1_success"
        ]
        is False
    )

    assert (
        result[
            "keyword_top1_success"
        ]
        is True
    )
