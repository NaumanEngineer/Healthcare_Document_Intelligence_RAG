"""Tests for Week 28 three-outcome governed RAG demo runner."""

from __future__ import annotations

from src.application.week28_demo_runner import (
    run_week28_three_outcome_demo,
)


def test_three_outcome_demo_runs_three_cases():
    report = (
        run_week28_three_outcome_demo()
    )

    assert report[
        "case_count"
    ] == 3

    assert len(
        report[
            "results"
        ]
    ) == 3


def test_three_outcome_demo_contains_expected_cases():
    report = (
        run_week28_three_outcome_demo()
    )

    outcomes = {
        result[
            "expected_outcome"
        ]
        for result in report[
            "results"
        ]
    }

    assert outcomes == {
        "ANSWER",
        "REVIEW_REQUIRED",
        "ABSTAIN",
    }


def test_actual_outcomes_match_expected_outcomes():
    report = (
        run_week28_three_outcome_demo()
    )

    for result in report[
        "results"
    ]:
        assert (
            result[
                "actual_outcome"
            ]
            == result[
                "expected_outcome"
            ]
        )


def test_every_case_reports_match():
    report = (
        run_week28_three_outcome_demo()
    )

    assert all(
        result[
            "matched"
        ]
        for result in report[
            "results"
        ]
    )


def test_all_cases_match_summary():
    report = (
        run_week28_three_outcome_demo()
    )

    assert report[
        "matched_case_count"
    ] == 3

    assert report[
        "all_cases_matched"
    ] is True


def test_cases_complete_without_failed_closed_status():
    report = (
        run_week28_three_outcome_demo()
    )

    for result in report[
        "results"
    ]:
        assert (
            result[
                "application_status"
            ]
            == "COMPLETED"
        )


def test_observability_completes_for_every_case():
    report = (
        run_week28_three_outcome_demo()
    )

    for result in report[
        "results"
    ]:
        assert (
            result[
                "observability_status"
            ]
            == "COMPLETED"
        )


def test_observability_records_events():
    report = (
        run_week28_three_outcome_demo()
    )

    for result in report[
        "results"
    ]:
        assert (
            result[
                "observed_event_count"
            ]
            > 0
        )


def test_runner_does_not_change_expected_outcome_into_actual_outcome():
    report = (
        run_week28_three_outcome_demo()
    )

    for result in report[
        "results"
    ]:
        canonical_result = (
            result[
                "result"
            ]
        )

        assert (
            result[
                "actual_outcome"
            ]
            == canonical_result.get(
                "final_outcome"
            )
        )