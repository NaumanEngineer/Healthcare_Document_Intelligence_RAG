from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.evaluation.validate_week25_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


def _load_benchmark() -> dict:
    with Path(BENCHMARK_PATH).open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_week25_benchmark_validates() -> None:
    benchmark = _load_benchmark()

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "validation_status"
    ] == "PASS"

    assert result[
        "case_count"
    ] == 18


def test_week25_case_ids_are_complete() -> None:
    benchmark = _load_benchmark()

    case_ids = {
        case["case_id"]
        for case in benchmark[
            "cases"
        ]
    }

    expected = {
        f"W25-C{number:03d}"
        for number in range(
            1,
            19,
        )
    }

    assert case_ids == expected


def test_week25_governance_distribution() -> None:
    benchmark = _load_benchmark()

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "governance_counts"
    ] == {
        "AUTO_ANSWER": 10,
        "REVIEW_REQUIRED": 6,
        "ABSTAIN": 2,
    }


def test_week25_verification_distribution() -> None:
    benchmark = _load_benchmark()

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "verification_counts"
    ] == {
        "PASS": 4,
        "REVIEW_REQUIRED": 13,
        "ABSTAIN": 1,
    }


def test_week25_overall_status_distribution() -> None:
    benchmark = _load_benchmark()

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "overall_status_counts"
    ] == {
        "PASS": 6,
        "PASS_WITH_WARNINGS": 0,
        "FAIL": 12,
    }


def test_duplicate_case_id_fails_closed() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][1][
        "case_id"
    ] = broken["cases"][0][
        "case_id"
    ]

    with pytest.raises(
        ValueError,
        match="duplicate case_id",
    ):
        validate_benchmark(
            broken
        )


def test_missing_case_fails_closed() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"] = broken[
        "cases"
    ][:-1]

    with pytest.raises(
        ValueError,
        match="expected exactly 18 cases",
    ):
        validate_benchmark(
            broken
        )


def test_invalid_governance_decision_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "expected_governance_decision"
    ] = "INVENTED_DECISION"

    with pytest.raises(
        ValueError,
        match="unsupported governance decision",
    ):
        validate_benchmark(
            broken
        )


def test_response_type_mismatch_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "expected_response_type"
    ] = "REVIEW"

    with pytest.raises(
        ValueError,
        match="requires response type",
    ):
        validate_benchmark(
            broken
        )


def test_duplicate_evidence_id_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    duplicate = copy.deepcopy(
        broken["cases"][1][
            "evidence_items"
        ][0]
    )

    broken["cases"][1][
        "evidence_items"
    ].append(
        duplicate
    )

    with pytest.raises(
        ValueError,
        match="duplicate evidence_id",
    ):
        validate_benchmark(
            broken
        )


def test_evidence_identity_mismatch_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "evidence_items"
    ][0][
        "evidence_id"
    ] = "EVIDENCE::WRONG"

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        validate_benchmark(
            broken
        )


def test_duplicate_citation_id_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    duplicate = copy.deepcopy(
        broken["cases"][1][
            "citation_index"
        ][0]
    )

    broken["cases"][1][
        "citation_index"
    ].append(
        duplicate
    )

    with pytest.raises(
        ValueError,
        match="duplicate citation ID",
    ):
        validate_benchmark(
            broken
        )


def test_citation_unknown_evidence_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "citation_index"
    ][0][
        "evidence_id"
    ] = "EVIDENCE::UNKNOWN"

    with pytest.raises(
        ValueError,
        match="references unknown evidence",
    ):
        validate_benchmark(
            broken
        )


def test_citation_evidence_document_mismatch_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "citation_index"
    ][0][
        "document_id"
    ] = "DOC-WRONG"

    with pytest.raises(
        ValueError,
        match="document_id does not match",
    ):
        validate_benchmark(
            broken
        )


def test_unknown_support_status_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "expected_claims"
    ][0][
        "expected_support_status"
    ] = "PERFECTLY_SUPPORTED"

    with pytest.raises(
        ValueError,
        match="unsupported status",
    ):
        validate_benchmark(
            broken
        )


def test_unknown_supporting_evidence_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "expected_claims"
    ][0][
        "supporting_evidence_ids"
    ] = [
        "EVIDENCE::UNKNOWN"
    ]

    with pytest.raises(
        ValueError,
        match="references unknown evidence",
    ):
        validate_benchmark(
            broken
        )


def test_required_citation_must_be_allowed() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "allowed_citation_ids"
    ] = []

    with pytest.raises(
        ValueError,
        match="required citations must also be allowed",
    ):
        validate_benchmark(
            broken
        )


def test_allowed_and_forbidden_citation_overlap_fails() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken["cases"][0][
        "forbidden_citation_ids"
    ] = [
        "E1"
    ]

    with pytest.raises(
        ValueError,
        match="both allowed and forbidden",
    ):
        validate_benchmark(
            broken
        )


def test_review_required_preserves_human_review() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    review_case = next(
        case
        for case in broken[
            "cases"
        ]
        if case[
            "expected_governance_decision"
        ]
        == "REVIEW_REQUIRED"
    )

    review_case[
        "requires_human_review"
    ] = False

    with pytest.raises(
        ValueError,
        match="must preserve human review",
    ):
        validate_benchmark(
            broken
        )


def test_auto_answer_can_escalate_after_verification() -> None:
    benchmark = _load_benchmark()

    auto_review_case = next(
        case
        for case in benchmark[
            "cases"
        ]
        if (
            case[
                "expected_governance_decision"
            ]
            == "AUTO_ANSWER"
            and case[
                "expected_verification_decision"
            ]
            == "REVIEW_REQUIRED"
        )
    )

    assert auto_review_case[
        "requires_human_review"
    ] is True

    result = validate_benchmark(
        benchmark
    )

    assert result[
        "validation_status"
    ] == "PASS"


def test_abstain_requires_abstention_flag() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    abstain_case = next(
        case
        for case in broken[
            "cases"
        ]
        if case[
            "expected_governance_decision"
        ]
        == "ABSTAIN"
    )

    abstain_case[
        "abstention_expected"
    ] = False

    with pytest.raises(
        ValueError,
        match="must set abstention_expected=true",
    ):
        validate_benchmark(
            broken
        )


def test_benchmark_is_synthetic_only() -> None:
    benchmark = _load_benchmark()

    broken = copy.deepcopy(
        benchmark
    )

    broken[
        "synthetic_data_only"
    ] = False

    with pytest.raises(
        ValueError,
        match="synthetic_data_only must be true",
    ):
        validate_benchmark(
            broken
        )