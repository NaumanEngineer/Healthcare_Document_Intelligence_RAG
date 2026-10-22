"""Tests for Week 28 three-outcome portfolio demo data."""

from __future__ import annotations

from src.application.week28_demo_data import (
    ABSTAIN_CASE_ID,
    ABSTAIN_QUESTION,
    ANSWER_CASE_ID,
    ANSWER_DOCUMENT_ID,
    ANSWER_QUESTION,
    REVIEW_CAPACITY_DOCUMENT_ID,
    REVIEW_CASE_ID,
    REVIEW_QUESTION,
    REVIEW_WORKFORCE_DOCUMENT_ID,
    build_abstain_corpus,
    build_answer_corpus,
    build_review_corpus,
    build_week28_demo_cases,
)


def _cases_by_id() -> dict[str, dict]:
    return {
        case["case_id"]: case
        for case in build_week28_demo_cases()
    }


def test_week28_demo_contains_three_cases():
    cases = build_week28_demo_cases()

    assert len(cases) == 3


def test_week28_demo_case_ids_are_unique():
    cases = build_week28_demo_cases()

    case_ids = [
        case["case_id"]
        for case in cases
    ]

    assert len(case_ids) == len(set(case_ids))


def test_answer_case_contract():
    cases = _cases_by_id()

    case = cases[
        ANSWER_CASE_ID
    ]

    assert case[
        "question"
    ] == ANSWER_QUESTION

    assert case[
        "expected_outcome"
    ] == "ANSWER"

    assert case[
        "synthetic_data"
    ] is True

    assert case[
        "patient_data_present"
    ] is False

    assert len(
        case[
            "chunks"
        ]
    ) == 1

    assert len(
        case[
            "embedded_chunks"
        ]
    ) == 1


def test_answer_case_has_expected_document():
    chunks, embedded_chunks = (
        build_answer_corpus()
    )

    assert len(chunks) == 1
    assert len(embedded_chunks) == 1

    assert chunks[0][
        "document_id"
    ] == ANSWER_DOCUMENT_ID

    assert embedded_chunks[0][
        "document_id"
    ] == ANSWER_DOCUMENT_ID


def test_review_case_contract():
    cases = _cases_by_id()

    case = cases[
        REVIEW_CASE_ID
    ]

    assert case[
        "question"
    ] == REVIEW_QUESTION

    assert case[
        "expected_outcome"
    ] == "REVIEW_REQUIRED"

    assert case[
        "synthetic_data"
    ] is True

    assert case[
        "patient_data_present"
    ] is False

    assert len(
        case[
            "chunks"
        ]
    ) == 2

    assert len(
        case[
            "embedded_chunks"
        ]
    ) == 2


def test_review_case_uses_two_distinct_documents():
    chunks, embedded_chunks = (
        build_review_corpus()
    )

    document_ids = {
        chunk[
            "document_id"
        ]
        for chunk in chunks
    }

    assert document_ids == {
        REVIEW_WORKFORCE_DOCUMENT_ID,
        REVIEW_CAPACITY_DOCUMENT_ID,
    }

    embedded_document_ids = {
        chunk[
            "document_id"
        ]
        for chunk in embedded_chunks
    }

    assert (
        embedded_document_ids
        == document_ids
    )


def test_review_documents_are_active():
    chunks, _ = (
        build_review_corpus()
    )

    assert all(
        chunk[
            "status"
        ] == "Active"
        for chunk in chunks
    )


def test_abstain_case_contract():
    cases = _cases_by_id()

    case = cases[
        ABSTAIN_CASE_ID
    ]

    assert case[
        "question"
    ] == ABSTAIN_QUESTION

    assert case[
        "expected_outcome"
    ] == "ABSTAIN"

    assert case[
        "synthetic_data"
    ] is True

    assert case[
        "patient_data_present"
    ] is False

    assert case[
        "chunks"
    ] == []

    assert case[
        "embedded_chunks"
    ] == []


def test_abstain_corpus_contains_no_manufactured_evidence():
    chunks, embedded_chunks = (
        build_abstain_corpus()
    )

    assert chunks == []
    assert embedded_chunks == []


def test_all_evidence_chunks_are_synthetic_non_patient_operational_guidance():
    cases = build_week28_demo_cases()

    chunks = [
        chunk
        for case in cases
        for chunk in case[
            "chunks"
        ]
    ]

    assert chunks

    for chunk in chunks:
        assert chunk[
            "document_type"
        ] == "operational_guidance"

        assert chunk[
            "source_type"
        ] == "synthetic_demo"

        assert chunk[
            "status"
        ] == "Active"

        assert chunk[
            "extraction_status"
        ] == "SUCCESS"

        assert chunk[
            "text"
        ]


def test_embedded_chunks_have_traceability_fields():
    cases = build_week28_demo_cases()

    embedded_chunks = [
        chunk
        for case in cases
        for chunk in case[
            "embedded_chunks"
        ]
    ]

    assert embedded_chunks

    for chunk in embedded_chunks:
        assert chunk[
            "vector"
        ]

        assert chunk[
            "embedding_model"
        ]

        assert chunk[
            "embedding_dimensions"
        ] == len(
            chunk[
                "vector"
            ]
        )

        assert chunk[
            "text_hash"
        ]