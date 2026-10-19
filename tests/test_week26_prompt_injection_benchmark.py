"""Integration tests for Week 26 prompt-injection benchmark."""

from __future__ import annotations

from src.evaluation.run_week26_prompt_injection_benchmark import (
    TARGET_CASE_ID,
    run_prompt_injection_benchmark,
)


def _result(
    report,
):
    return report[
        "results"
    ][0]


def test_prompt_injection_benchmark_targets_c009():
    report = (
        run_prompt_injection_benchmark()
    )

    assert report[
        "target_case_id"
    ] == TARGET_CASE_ID

    assert report[
        "summary"
    ][
        "case_count"
    ] == 1


def test_prompt_injection_case_matches():
    report = (
        run_prompt_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "matched_case_count"
    ] == 1

    assert report[
        "summary"
    ][
        "mismatched_case_count"
    ] == 0

    assert report[
        "summary"
    ][
        "match_rate"
    ] == 1.0


def test_c009_detects_prompt_injection():
    report = (
        run_prompt_injection_benchmark()
    )

    result = _result(
        report
    )

    assert result[
        "actual_injection_detected"
    ] is True


def test_c009_matches_expected_injection_decision():
    report = (
        run_prompt_injection_benchmark()
    )

    result = _result(
        report
    )

    assert (
        result[
            "actual_prompt_injection_decision"
        ]
        == result[
            "expected_prompt_injection_decision"
        ]
    )


def test_c009_preserves_attack_source_id():
    report = (
        run_prompt_injection_benchmark()
    )

    result = _result(
        report
    )

    assert result[
        "injection_evidence_ids"
    ]


def test_prompt_injection_benchmark_has_no_mismatches():
    report = (
        run_prompt_injection_benchmark()
    )

    assert report[
        "summary"
    ][
        "mismatched_case_ids"
    ] == []