"""Integration tests for Week 26 version/temporal benchmark."""

from __future__ import annotations

from src.evaluation.run_week26_version_temporal_benchmark import (
    TARGET_CASE_IDS,
    run_version_temporal_benchmark,
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


def test_temporal_benchmark_targets_expected_cases():
    report = (
        run_version_temporal_benchmark()
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
    ] == 2


def test_temporal_benchmark_matches_both_cases():
    report = (
        run_version_temporal_benchmark()
    )

    summary = report[
        "summary"
    ]

    assert summary[
        "matched_case_count"
    ] == 2

    assert summary[
        "mismatched_case_count"
    ] == 0

    assert summary[
        "match_rate"
    ] == 1.0


def test_c004_detects_version_succession():
    report = (
        run_version_temporal_benchmark()
    )

    case = _case(
        report,
        "W26-C004",
    )

    assert case[
        "version_match"
    ] is True

    assert (
        case[
            "explicit_replacement_detected"
        ]
        or bool(
            {
                "PREVIOUS_VERSION",
                "POSSIBLE_REPLACEMENT",
            }
            & set(
                case[
                    "actual_version_relationships"
                ]
            )
        )
    )


def test_c004_contains_non_current_evidence():
    report = (
        run_version_temporal_benchmark()
    )

    case = _case(
        report,
        "W26-C004",
    )

    assert (
        "TEMPORALLY_EXPIRED"
        in case[
            "actual_temporal_states"
        ]
        or "TEMPORALLY_HISTORICAL"
        in case[
            "actual_temporal_states"
        ]
    )


def test_c005_detects_expired_evidence():
    report = (
        run_version_temporal_benchmark()
    )

    case = _case(
        report,
        "W26-C005",
    )

    assert (
        "TEMPORALLY_EXPIRED"
        in case[
            "actual_temporal_states"
        ]
        or "TEMPORALLY_HISTORICAL"
        in case[
            "actual_temporal_states"
        ]
    )


def test_temporal_cases_do_not_report_clean_current_only_state():
    report = (
        run_version_temporal_benchmark()
    )

    for case in report[
        "results"
    ]:
        assert case[
            "assurance_decision"
        ] != "SAFE_FOR_CURRENT_USE"


def test_no_temporal_benchmark_mismatches():
    report = (
        run_version_temporal_benchmark()
    )

    assert report[
        "summary"
    ][
        "mismatched_case_ids"
    ] == []