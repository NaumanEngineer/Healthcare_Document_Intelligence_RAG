"""Integration tests for Week 26 C011 abstention safety."""

from __future__ import annotations

from src.evaluation.run_week26_abstention_safety_benchmark import (
    TARGET_CASE_ID,
    run_abstention_safety_benchmark,
)


def _result(
    report,
):
    return report[
        "results"
    ][0]


def test_abstention_benchmark_targets_c011():
    report = (
        run_abstention_safety_benchmark()
    )

    assert report[
        "target_case_id"
    ] == TARGET_CASE_ID

    assert report[
        "summary"
    ][
        "case_count"
    ] == 1


def test_c011_matches_expected_abstention_state():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert (
        result[
            "actual_abstention_decision"
        ]
        == "DIRECTIVE_LEAKAGE"
    )

    assert (
        result[
            "actual_abstention_decision"
        ]
        == result[
            "expected_abstention_decision"
        ]
    )


def test_c011_detects_directive_leakage():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert result[
        "directive_leakage_detected"
    ] is True


def test_c011_abstention_structure_remains_present():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert result[
        "structure_valid"
    ] is True


def test_c011_final_governance_remains_abstain():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert (
        result[
            "expected_governance_decision"
        ]
        == "ABSTAIN"
    )

    assert (
        result[
            "actual_final_assurance_decision"
        ]
        == "ABSTAIN"
    )


def test_c011_content_violation_does_not_upgrade_authority():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert (
        result[
            "actual_final_assurance_decision"
        ]
        != "PASS"
    )


def test_c011_violation_flag_matches_benchmark():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert result[
        "expected_abstention_violation"
    ] is True

    assert result[
        "actual_abstention_violation"
    ] is True


def test_c011_unsafe_section_is_identified():
    report = (
        run_abstention_safety_benchmark()
    )

    result = _result(
        report
    )

    assert (
        "what_is_needed_to_continue"
        in result[
            "directive_sections"
        ]
    )


def test_abstention_benchmark_has_no_mismatches():
    report = (
        run_abstention_safety_benchmark()
    )

    assert report[
        "summary"
    ][
        "matched_case_count"
    ] == 1

    assert report[
        "summary"
    ][
        "mismatched_case_ids"
    ] == []