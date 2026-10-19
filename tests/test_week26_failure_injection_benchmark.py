"""Tests for Week 26 failure-injection benchmark."""

from __future__ import annotations

from src.evaluation.run_week26_failure_injection_benchmark import (
    run_failure_injection_benchmark,
)


def test_failure_injection_benchmark_has_eleven_cases():
    report = (
        run_failure_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "case_count"
    ] == 11


def test_all_failure_injection_cases_match():
    report = (
        run_failure_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "matched_case_count"
    ] == 11

    assert report[
        "summary"
    ][
        "mismatched_case_count"
    ] == 0


def test_no_failure_case_produces_unsafe_pass():
    report = (
        run_failure_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "unsafe_pass_case_ids"
    ] == []


def test_malformed_cases_fail_closed():
    report = (
        run_failure_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "fail_closed_case_count"
    ] >= 10


def test_control_case_remains_normal_assurance():
    report = (
        run_failure_injection_benchmark()
    )

    result = next(
        item
        for item
        in report[
            "results"
        ]
        if item[
            "case_id"
        ]
        == "W26-FI-010"
    )

    assert (
        result[
            "actual_boundary_status"
        ]
        == "NORMAL_ASSURANCE"
    )

    assert (
        result[
            "actual_final_decision"
        ]
        == "REVIEW_REQUIRED"
    )


def test_invalid_collection_fails_closed():
    report = (
        run_failure_injection_benchmark()
    )

    result = next(
        item
        for item
        in report[
            "results"
        ]
        if item[
            "case_id"
        ]
        == "W26-FI-011"
    )

    assert (
        result[
            "actual_boundary_status"
        ]
        == "FAIL_CLOSED"
    )

    assert (
        result[
            "actual_final_decision"
        ]
        == "ABSTAIN"
    )


def test_overall_failure_injection_status_passes():
    report = (
        run_failure_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "overall_status"
    ] == "PASS"