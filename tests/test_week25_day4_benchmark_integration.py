import json

from src.evaluation.run_week25_day4_faithfulness_benchmark import (
    _audit_conflict_coverage,
    _derive_expected_integrated_decision,
    _load_benchmark,
    _run_case,
)


def _case(
    case_id,
):
    benchmark = _load_benchmark()

    return next(
        case
        for case
        in benchmark[
            "cases"
        ]
        if case[
            "case_id"
        ]
        == case_id
    )


def test_clean_auto_answer_passes():
    result = _run_case(
        _case(
            "W25-C001"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "actual_integrated_decision"
    ] == "PASS"


def test_unsupported_operational_claim_is_caught():
    result = _run_case(
        _case(
            "W25-C007"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "actual_integrated_decision"
    ] == "REVIEW_REQUIRED"

    assert result[
        "hallucination_risk_count"
    ] > 0


def test_overstated_claim_is_caught():
    result = _run_case(
        _case(
            "W25-C009"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "overstatement_count"
    ] > 0


def test_safe_conflict_statement_preserves_both_sources():
    case = _case(
        "W25-C012"
    )

    conflict = (
        _audit_conflict_coverage(
            case
        )
    )

    assert conflict[
        "applicable"
    ] is True

    assert conflict[
        "conflict_ignored"
    ] is False


def test_ignored_conflict_is_detected():
    result = _run_case(
        _case(
            "W25-C013"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "conflict_ignored_detected"
    ] is True


def test_hidden_uncertainty_is_detected():
    result = _run_case(
        _case(
            "W25-C014"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "overstatement_count"
    ] > 0


def test_review_authority_increase_is_detected():
    result = _run_case(
        _case(
            "W25-C015"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert (
        result[
            "review_authority_increase_detected"
        ]
        is True
    )


def test_safe_abstention_remains_abstain():
    result = _run_case(
        _case(
            "W25-C016"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "actual_integrated_decision"
    ] == "ABSTAIN"

    assert (
        result[
            "abstention_violation_detected"
        ]
        is False
    )


def test_unsafe_abstention_is_detected():
    result = _run_case(
        _case(
            "W25-C017"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "actual_integrated_decision"
    ] == "ABSTAIN"

    assert (
        result[
            "abstention_violation_detected"
        ]
        is True
    )


def test_fabricated_threshold_is_caught():
    result = _run_case(
        _case(
            "W25-C018"
        )
    )

    assert result[
        "benchmark_match"
    ] is True

    assert result[
        "actual_integrated_decision"
    ] == "REVIEW_REQUIRED"

    assert result[
        "hallucination_risk_count"
    ] > 0


def test_expected_governance_boundaries():
    assert (
        _derive_expected_integrated_decision(
            _case(
                "W25-C001"
            )
        )
        == "PASS"
    )

    assert (
        _derive_expected_integrated_decision(
            _case(
                "W25-C015"
            )
        )
        == "REVIEW_REQUIRED"
    )

    assert (
        _derive_expected_integrated_decision(
            _case(
                "W25-C016"
            )
        )
        == "ABSTAIN"
    )


def test_all_eighteen_cases_match():
    benchmark = _load_benchmark()

    results = [
        _run_case(
            case
        )
        for case
        in benchmark[
            "cases"
        ]
    ]

    failed = [
        {
            "case_id": result[
                "case_id"
            ],
            "failure_reasons": result[
                "failure_reasons"
            ],
        }
        for result
        in results
        if not result[
            "benchmark_match"
        ]
    ]

    assert failed == [], json.dumps(
        failed,
        indent=2,
    )