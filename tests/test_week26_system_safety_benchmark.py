"""Integration tests for Week 26 end-to-end system safety."""

from __future__ import annotations

from src.evaluation.run_week26_system_safety_benchmark import (
    run_system_safety_benchmark,
)


def test_system_safety_benchmark_covers_all_cases():
    report = (
        run_system_safety_benchmark()
    )

    assert report[
        "summary"
    ][
        "case_count"
    ] == 12


def test_all_cases_pass_system_invariants():
    report = (
        run_system_safety_benchmark()
    )

    assert report[
        "summary"
    ][
        "passed_case_count"
    ] == 12

    assert report[
        "summary"
    ][
        "failed_case_count"
    ] == 0


def test_no_system_safety_failures():
    report = (
        run_system_safety_benchmark()
    )

    assert report[
        "summary"
    ][
        "failed_case_ids"
    ] == []


def test_overall_system_safety_status_is_pass():
    report = (
        run_system_safety_benchmark()
    )

    assert report[
        "summary"
    ][
        "overall_status"
    ] == "PASS"


def test_no_case_increases_authority():
    report = (
        run_system_safety_benchmark()
    )

    for result in report[
        "results"
    ]:
        assert result[
            "checks"
        ][
            "authority_not_increased"
        ] is True


def test_unsafe_cases_never_pass():
    report = (
        run_system_safety_benchmark()
    )

    for result in report[
        "results"
    ]:
        if result[
            "unsafe_signal_present"
        ]:
            assert result[
                "final_decision"
            ] != "PASS"


def test_abstain_case_remains_abstain():
    report = (
        run_system_safety_benchmark()
    )

    abstain_cases = [
        result
        for result
        in report[
            "results"
        ]
        if result[
            "upstream_decision"
        ]
        == "ABSTAIN"
    ]

    assert abstain_cases

    for result in abstain_cases:
        assert result[
            "final_decision"
        ] == "ABSTAIN"