"""Tests for unified Week 26 adversarial assurance."""

from __future__ import annotations

from src.evaluation.run_week26_assurance_suite import (
    ALL_EXPECTED_CASE_IDS,
    ANCHOR_CASE_IDS,
    DEDICATED_CASE_IDS,
    run_week26_assurance_suite,
)


def test_suite_covers_all_twelve_cases():
    report = (
        run_week26_assurance_suite()
    )

    assert report[
        "summary"
    ][
        "case_count"
    ] == 12

    assert {
        item[
            "case_id"
        ]
        for item
        in report[
            "case_register"
        ]
    } == ALL_EXPECTED_CASE_IDS


def test_dedicated_and_anchor_coverage_is_complete():
    assert len(
        DEDICATED_CASE_IDS
    ) == 9

    assert len(
        ANCHOR_CASE_IDS
    ) == 3

    assert not (
        DEDICATED_CASE_IDS
        & ANCHOR_CASE_IDS
    )

    assert (
        DEDICATED_CASE_IDS
        | ANCHOR_CASE_IDS
    ) == ALL_EXPECTED_CASE_IDS


def test_all_cases_match():
    report = (
        run_week26_assurance_suite()
    )

    assert report[
        "summary"
    ][
        "matched_case_count"
    ] == 12

    assert report[
        "summary"
    ][
        "mismatched_case_count"
    ] == 0

    assert report[
        "summary"
    ][
        "mismatched_case_ids"
    ] == []


def test_original_baseline_preserved_final_governance():
    report = (
        run_week26_assurance_suite()
    )

    assert report[
        "baseline_final_governance"
    ][
        "all_final_decisions_match"
    ] is True

    assert report[
        "baseline_final_governance"
    ][
        "mismatch_case_ids"
    ] == []


def test_regression_anchor_cases_match_claim_and_final_states():
    report = (
        run_week26_assurance_suite()
    )

    anchors = {
        item[
            "case_id"
        ]: item
        for item
        in report[
            "case_register"
        ]
        if item[
            "case_id"
        ]
        in ANCHOR_CASE_IDS
    }

    for case_id in ANCHOR_CASE_IDS:
        result = anchors[
            case_id
        ]

        assert result[
            "matched"
        ] is True

        assert result[
            "claim_statuses_match"
        ] is True

        assert result[
            "final_decision_matches"
        ] is True


def test_dedicated_control_cases_all_match():
    report = (
        run_week26_assurance_suite()
    )

    dedicated = [
        item
        for item
        in report[
            "case_register"
        ]
        if item[
            "case_id"
        ]
        in DEDICATED_CASE_IDS
    ]

    assert len(
        dedicated
    ) == 9

    assert all(
        item[
            "matched"
        ]
        for item
        in dedicated
    )


def test_overall_status_is_pass():
    report = (
        run_week26_assurance_suite()
    )

    assert report[
        "summary"
    ][
        "overall_status"
    ] == "PASS"