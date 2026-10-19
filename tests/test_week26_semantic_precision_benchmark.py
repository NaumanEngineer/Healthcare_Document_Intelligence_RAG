"""Integration tests for the Week 26 semantic precision benchmark."""

from __future__ import annotations

from src.evaluation.run_week26_semantic_precision_benchmark import (
    TARGET_CASE_IDS,
    run_semantic_precision_benchmark,
)


def _case(
    report,
    case_id,
):
    return next(
        result
        for result
        in report[
            "results"
        ]
        if result[
            "case_id"
        ]
        == case_id
    )


def _claim(
    case,
    claim_id,
):
    return next(
        result
        for result
        in case[
            "claim_results"
        ]
        if result[
            "claim_id"
        ]
        == claim_id
    )


def test_semantic_benchmark_targets_expected_cases():
    report = (
        run_semantic_precision_benchmark()
    )

    assert report[
        "target_case_ids"
    ] == list(
        TARGET_CASE_IDS
    )

    assert report[
        "summary"
    ][
        "case_count"
    ] == 3


def test_semantic_benchmark_matches_all_target_cases():
    report = (
        run_semantic_precision_benchmark()
    )

    summary = report[
        "summary"
    ]

    assert summary[
        "matched_case_count"
    ] == 3

    assert summary[
        "mismatched_case_count"
    ] == 0

    assert summary[
        "match_rate"
    ] == 1.0


def test_c003_partial_support_is_corrected():
    report = (
        run_semantic_precision_benchmark()
    )

    case = _case(
        report,
        "W26-C003",
    )

    claim = _claim(
        case,
        "W26-C003-CL3",
    )

    assert (
        claim[
            "baseline_support_status"
        ]
        == "SUPPORTED"
    )

    assert (
        claim[
            "revised_support_status"
        ]
        == "PARTIALLY_SUPPORTED"
    )

    assert claim[
        "modal_strengthening_detected"
    ] is True


def test_c003_unsupported_immediate_claim_is_not_upgraded():
    report = (
        run_semantic_precision_benchmark()
    )

    case = _case(
        report,
        "W26-C003",
    )

    claim = _claim(
        case,
        "W26-C003-CL4",
    )

    assert (
        claim[
            "baseline_support_status"
        ]
        == "UNSUPPORTED"
    )

    assert (
        claim[
            "revised_support_status"
        ]
        == "UNSUPPORTED"
    )

    assert claim[
        "support_authority_not_increased"
    ] is True


def test_c007_role_hallucination_is_reduced_to_unsupported():
    report = (
        run_semantic_precision_benchmark()
    )

    case = _case(
        report,
        "W26-C007",
    )

    claim = _claim(
        case,
        "W26-C007-CL1",
    )

    assert (
        claim[
            "baseline_support_status"
        ]
        == "PARTIALLY_SUPPORTED"
    )

    assert (
        claim[
            "revised_support_status"
        ]
        == "UNSUPPORTED"
    )

    assert claim[
        "role_responsibility_unsupported"
    ] is True


def test_c008_modal_strengthening_is_reduced_to_partial():
    report = (
        run_semantic_precision_benchmark()
    )

    case = _case(
        report,
        "W26-C008",
    )

    claim = _claim(
        case,
        "W26-C008-CL1",
    )

    assert (
        claim[
            "baseline_support_status"
        ]
        == "SUPPORTED"
    )

    assert (
        claim[
            "revised_support_status"
        ]
        == "PARTIALLY_SUPPORTED"
    )

    assert claim[
        "modal_strengthening_detected"
    ] is True


def test_semantic_precision_never_increases_support_authority():
    report = (
        run_semantic_precision_benchmark()
    )

    assert report[
        "summary"
    ][
        "authority_increase_violation_claim_ids"
    ] == []


def test_expected_cases_have_no_mismatches():
    report = (
        run_semantic_precision_benchmark()
    )

    assert report[
        "summary"
    ][
        "mismatched_case_ids"
    ] == []