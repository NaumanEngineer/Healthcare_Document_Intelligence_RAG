"""Focused Week 26 version and temporal benchmark.

Targets:

    W26-C004 - Superseded and Active Version Chain
    W26-C005 - Temporal Validity Failure

The purpose is to prove that the new Week 26 temporal/version layer
explains why evidence is historical, expired, current, or replaced.

It does not replace the existing lifecycle guard.

Run with:

    python -m src.evaluation.run_week26_version_temporal_benchmark
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)
from src.evaluation.version_temporal_assurance import (
    assess_version_temporal_assurance,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_version_temporal_benchmark.json"
)


TARGET_CASE_IDS = (
    "W26-C004",
    "W26-C005",
)


def _load_benchmark() -> dict[str, Any]:
    """Load and validate the authoritative Week 26 benchmark."""

    with Path(
        BENCHMARK_PATH
    ).open(
        "r",
        encoding="utf-8",
    ) as file:
        benchmark = json.load(
            file
        )

    validate_benchmark(
        benchmark
    )

    return benchmark


def _target_cases(
    benchmark: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return focused temporal/version cases in fixed order."""

    cases_by_id = {
        case[
            "case_id"
        ]: case
        for case
        in benchmark[
            "cases"
        ]
    }

    missing = [
        case_id
        for case_id
        in TARGET_CASE_IDS
        if case_id
        not in cases_by_id
    ]

    if missing:
        raise ValueError(
            "Week 26 temporal benchmark missing cases: "
            f"{missing}"
        )

    return [
        cases_by_id[
            case_id
        ]
        for case_id
        in TARGET_CASE_IDS
    ]


def _expected_temporal_states(
    case: dict[str, Any],
) -> set[str]:
    """Return expected temporal states declared by claim expectations."""

    states = {
        result[
            "expected_temporal_validity"
        ]
        for result
        in case[
            "expected_claim_results"
        ]
        if result.get(
            "expected_temporal_validity"
        )
        not in {
            None,
            "NOT_APPLICABLE",
        }
    }

    return states


def _actual_temporal_states(
    assurance: dict[str, Any],
) -> set[str]:
    """Return actual temporal states from evaluator output."""

    return {
        result[
            "temporal_state"
        ]
        for result
        in assurance[
            "temporal_results"
        ]
    }


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run one benchmark case through temporal/version assurance."""

    query_date = case[
        "query_date"
    ]

    assurance = (
        assess_version_temporal_assurance(
            evidence_items=case[
                "evidence_items"
            ],
            query_date=query_date,
        )
    )

    expected_temporal = (
        _expected_temporal_states(
            case
        )
    )

    actual_temporal = (
        _actual_temporal_states(
            assurance
        )
    )

    temporal_match = (
        expected_temporal.issubset(
            actual_temporal
        )
    )

    expected_version_relationship = (
        case.get(
            "expected_relationship_result"
        )
    )

    actual_version_relationships = {
        result[
            "relationship"
        ]
        for result
        in assurance[
            "version_results"
        ]
    }

    version_match = True

    if expected_version_relationship in {
        "VERSION_SUCCESSION",
    }:
        version_match = bool(
            {
                "EXPLICIT_REPLACEMENT",
                "PREVIOUS_VERSION",
                "POSSIBLE_REPLACEMENT",
            }
            & actual_version_relationships
        )

    failure_reasons = []

    if not temporal_match:
        failure_reasons.append(
            "Temporal-state mismatch: "
            f"expected at least {sorted(expected_temporal)}, "
            f"got {sorted(actual_temporal)}"
        )

    if not version_match:
        failure_reasons.append(
            "Version relationship mismatch: "
            f"expected {expected_version_relationship}, "
            f"got {sorted(actual_version_relationships)}"
        )

    return {
        "case_id": case[
            "case_id"
        ],
        "case_name": case[
            "case_name"
        ],
        "query_date": query_date,
        "expected_temporal_states": sorted(
            expected_temporal
        ),
        "actual_temporal_states": sorted(
            actual_temporal
        ),
        "expected_relationship_result": (
            expected_version_relationship
        ),
        "actual_version_relationships": sorted(
            actual_version_relationships
        ),
        "assurance_decision": assurance[
            "decision"
        ],
        "explicit_replacement_detected": assurance[
            "explicit_replacement_detected"
        ],
        "current_evidence_ids": assurance[
            "current_evidence_ids"
        ],
        "historical_evidence_ids": assurance[
            "historical_evidence_ids"
        ],
        "temporal_match": temporal_match,
        "version_match": version_match,
        "case_match": (
            temporal_match
            and version_match
        ),
        "assurance": assurance,
        "failure_reasons": (
            failure_reasons
        ),
    }


def _summarise(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarise focused temporal/version benchmark."""

    matched = [
        result
        for result
        in results
        if result[
            "case_match"
        ]
    ]

    mismatched = [
        result
        for result
        in results
        if not result[
            "case_match"
        ]
    ]

    expired_cases = []

    historical_cases = []

    replacement_cases = []

    for result in results:
        case_id = result[
            "case_id"
        ]

        if (
            "TEMPORALLY_EXPIRED"
            in result[
                "actual_temporal_states"
            ]
        ):
            expired_cases.append(
                case_id
            )

        if (
            "TEMPORALLY_HISTORICAL"
            in result[
                "actual_temporal_states"
            ]
        ):
            historical_cases.append(
                case_id
            )

        if result[
            "explicit_replacement_detected"
        ]:
            replacement_cases.append(
                case_id
            )

    return {
        "case_count": len(
            results
        ),
        "matched_case_count": len(
            matched
        ),
        "mismatched_case_count": len(
            mismatched
        ),
        "match_rate": (
            round(
                len(
                    matched
                )
                / len(
                    results
                ),
                4,
            )
            if results
            else 0.0
        ),
        "expired_case_ids": sorted(
            set(
                expired_cases
            )
        ),
        "historical_case_ids": sorted(
            set(
                historical_cases
            )
        ),
        "explicit_replacement_case_ids": sorted(
            set(
                replacement_cases
            )
        ),
        "mismatched_case_ids": [
            result[
                "case_id"
            ]
            for result
            in mismatched
        ],
    }


def run_version_temporal_benchmark() -> dict[str, Any]:
    """Execute focused Week 26 temporal/version benchmark."""

    benchmark = _load_benchmark()

    cases = _target_cases(
        benchmark
    )

    results = [
        _run_case(
            case
        )
        for case
        in cases
    ]

    summary = _summarise(
        results
    )

    report = {
        "benchmark_name": (
            "Week 26 Version and Temporal Benchmark"
        ),
        "benchmark_version": "1.0",
        "source_benchmark": benchmark[
            "benchmark_name"
        ],
        "evaluation_type": (
            "week26_version_temporal_hardening"
        ),
        "target_case_ids": list(
            TARGET_CASE_IDS
        ),
        "summary": summary,
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return report


def _print_summary(
    report: dict[str, Any],
) -> None:
    """Print concise benchmark evidence."""

    summary = report[
        "summary"
    ]

    print(
        "Week 26 Version and Temporal Benchmark"
    )

    print(
        "--------------------------------------"
    )

    print(
        f"Cases: {summary['case_count']}"
    )

    print(
        f"Matched: {summary['matched_case_count']}"
    )

    print(
        f"Mismatched: {summary['mismatched_case_count']}"
    )

    print(
        f"Match rate: {summary['match_rate']:.1%}"
    )

    print(
        "Expired cases: "
        f"{summary['expired_case_ids']}"
    )

    print(
        "Historical cases: "
        f"{summary['historical_case_ids']}"
    )

    print(
        "Explicit replacement cases: "
        f"{summary['explicit_replacement_case_ids']}"
    )

    print(
        "Mismatched cases: "
        f"{summary['mismatched_case_ids']}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


def main() -> None:
    """CLI entry point."""

    report = (
        run_version_temporal_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()