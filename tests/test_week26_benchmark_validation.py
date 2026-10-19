"""Tests for the Week 26 adversarial benchmark validator."""

from __future__ import annotations

from copy import deepcopy

import pytest

from src.evaluation.validate_week26_benchmark import (
    EXPECTED_CASE_COUNT,
    EXPECTED_CASE_IDS,
    load_benchmark,
    validate_benchmark,
)


def _load_valid_benchmark():
    return load_benchmark()


def test_week26_benchmark_validates_successfully():
    benchmark = _load_valid_benchmark()

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "validation_status"
    ] == "PASS"

    assert result[
        "case_count"
    ] == EXPECTED_CASE_COUNT


def test_week26_case_ids_are_exact_and_sequential():
    benchmark = _load_valid_benchmark()

    case_ids = [
        case["case_id"]
        for case in benchmark["cases"]
    ]

    assert case_ids == EXPECTED_CASE_IDS


def test_week26_benchmark_is_synthetic_only():
    benchmark = _load_valid_benchmark()

    assert benchmark[
        "synthetic_data_only"
    ] is True


def test_week26_rejects_missing_case():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ].pop()

    with pytest.raises(
        ValueError,
        match="exactly 12 cases",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_non_sequential_case_ids():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][0][
        "case_id"
    ] = "W26-C999"

    with pytest.raises(
        ValueError,
        match="case IDs must be sequential",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_duplicate_case_ids():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][1][
        "case_id"
    ] = benchmark[
        "cases"
    ][0][
        "case_id"
    ]

    with pytest.raises(
        ValueError,
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_unknown_evidence_reference():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][0][
        "citation_index"
    ][0][
        "evidence_id"
    ] = "UNKNOWN-EVIDENCE"

    with pytest.raises(
        ValueError,
        match="references unknown evidence",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_unknown_claim_citation():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][0][
        "candidate_claims"
    ][0][
        "citation_ids"
    ] = [
        "UNKNOWN-CITATION"
    ]

    with pytest.raises(
        ValueError,
        match="references unknown citation",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_invalid_lifecycle_status():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][0][
        "evidence_items"
    ][0][
        "status"
    ] = "current"

    with pytest.raises(
        ValueError,
        match="invalid evidence status",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_invalid_date_format():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][3][
        "query_date"
    ] = "15-04-2026"

    with pytest.raises(
        ValueError,
        match="YYYY-MM-DD",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_rejects_governance_response_mismatch():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][0][
        "expected_response_type"
    ] = "REVIEW"

    with pytest.raises(
        ValueError,
        match="response type does not match governance",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_review_governance_cannot_be_upgraded_to_pass():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    review_case = next(
        case
        for case in benchmark[
            "cases"
        ]
        if case[
            "expected_governance_decision"
        ]
        == "REVIEW_REQUIRED"
    )

    review_case[
        "expected_final_assurance_decision"
    ] = "PASS"

    with pytest.raises(
        ValueError,
        match="illegally increases review governance",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_abstain_governance_cannot_be_upgraded():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    abstain_case = next(
        case
        for case in benchmark[
            "cases"
        ]
        if case[
            "expected_governance_decision"
        ]
        == "ABSTAIN"
    )

    abstain_case[
        "expected_final_assurance_decision"
    ] = "REVIEW_REQUIRED"

    with pytest.raises(
        ValueError,
        match="illegally increases abstention governance",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_prompt_injection_flag_requires_tag():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    injection_case = next(
        case
        for case in benchmark[
            "cases"
        ]
        if case[
            "prompt_injection_expected"
        ]
    )

    injection_case[
        "benchmark_tags"
    ] = [
        tag
        for tag in injection_case[
            "benchmark_tags"
        ]
        if tag != "prompt_injection"
    ]

    with pytest.raises(
        ValueError,
        match="lacks prompt_injection tag",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_abstention_violation_requires_abstain_governance():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    abstain_case = next(
        case
        for case in benchmark[
            "cases"
        ]
        if case[
            "abstention_violation_expected"
        ]
    )

    abstain_case[
        "expected_governance_decision"
    ] = "AUTO_ANSWER"

    abstain_case[
        "expected_response_type"
    ] = "ANSWER"

    with pytest.raises(
        ValueError,
        match="abstention violation requires ABSTAIN governance",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_expected_claim_results_cover_all_claims():
    benchmark = deepcopy(
        _load_valid_benchmark()
    )

    benchmark[
        "cases"
    ][0][
        "expected_claim_results"
    ] = []

    with pytest.raises(
        ValueError,
        match="do not cover all candidate claims exactly once",
    ):
        validate_benchmark(
            benchmark
        )


def test_week26_summary_counts_are_stable():
    benchmark = _load_valid_benchmark()

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "governance_counts"
    ] == {
        "ABSTAIN": 1,
        "AUTO_ANSWER": 7,
        "REVIEW_REQUIRED": 4,
    }

    assert result[
        "final_decision_counts"
    ] == {
        "ABSTAIN": 1,
        "PASS": 0,
        "REVIEW_REQUIRED": 11,
    }

    assert result[
        "prompt_injection_case_count"
    ] == 1

    assert result[
        "abstention_violation_case_count"
    ] == 1

    assert result[
        "conflict_case_count"
    ] == 3

    assert result[
        "human_review_count"
    ] == 12