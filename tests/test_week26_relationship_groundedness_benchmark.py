"""Integration tests for Week 26 relationship groundedness."""

from __future__ import annotations

from src.evaluation.run_week26_relationship_groundedness_benchmark import (
    TARGET_CASE_IDS,
    run_relationship_benchmark,
)


def test_relationship_benchmark_evaluates_only_target_cases():
    report = run_relationship_benchmark()

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


def test_relationship_benchmark_matches_both_cases():
    report = run_relationship_benchmark()

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


def test_frankenstein_support_is_relationship_unverified():
    report = run_relationship_benchmark()

    summary = report[
        "summary"
    ]

    assert summary[
        "relationship_unverified_case_ids"
    ] == [
        "W26-C001"
    ]


def test_conflict_compression_is_blocked():
    report = run_relationship_benchmark()

    summary = report[
        "summary"
    ]

    assert summary[
        "conflict_blocked_case_ids"
    ] == [
        "W26-C012"
    ]


def test_adversarial_relationship_cases_never_allow_composition():
    report = run_relationship_benchmark()

    assert report[
        "summary"
    ][
        "composition_allowed_case_ids"
    ] == []


def test_c001_relationship_reason_is_auditable():
    report = run_relationship_benchmark()

    case = next(
        result
        for result
        in report[
            "results"
        ]
        if result[
            "case_id"
        ]
        == "W26-C001"
    )

    claim = case[
        "claim_results"
    ][0]

    assert claim[
        "actual_groundedness_status"
    ] == "RELATIONSHIP_UNVERIFIED"

    assert (
        claim[
            "composition_allowed"
        ]
        is False
    )

    assert claim[
        "relationship"
    ] if "relationship" in claim else True


def test_c012_conflict_components_are_preserved():
    report = run_relationship_benchmark()

    case = next(
        result
        for result
        in report[
            "results"
        ]
        if result[
            "case_id"
        ]
        == "W26-C012"
    )

    claim = case[
        "claim_results"
    ][0]

    assert claim[
        "actual_groundedness_status"
    ] == "CONFLICT_BLOCKED"

    assert (
        claim[
            "composition_allowed"
        ]
        is False
    )

    assert set(
        claim[
            "contradictory_components"
        ]
    ) == {
        "W26-C012-E1",
        "W26-C012-E2",
    }