"""Focused Week 26 relationship-aware groundedness benchmark.

This runner evaluates the two primary Week 26 evidence-relationship
cases:

    W26-C001 - Frankenstein Multi-Source Support
    W26-C012 - Conflict Compression

It is intentionally narrow.

The purpose is to prove the new standalone relationship-aware
groundedness control before integrating it into the wider Week 26
assurance pipeline.

Run with:

    python -m src.evaluation.run_week26_relationship_groundedness_benchmark
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


from src.evaluation.relationship_aware_groundedness import (
    assess_relationship_aware_groundedness,
)
from src.evaluation.validate_week26_benchmark import (
    BENCHMARK_PATH,
    validate_benchmark,
)


OUTPUT_PATH = (
    ROOT
    / "outputs"
    / "week26_relationship_groundedness_benchmark.json"
)


TARGET_CASE_IDS = (
    "W26-C001",
    "W26-C012",
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
    """Return the focused relationship cases in required order."""

    cases_by_id = {
        case["case_id"]: case
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
            "Week 26 relationship benchmark is missing "
            f"required cases: {missing}"
        )

    return [
        cases_by_id[
            case_id
        ]
        for case_id
        in TARGET_CASE_IDS
    ]


def _expected_claim_result_lookup(
    case: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Index expected claim results by claim ID."""

    return {
        result[
            "claim_id"
        ]: result
        for result
        in case[
            "expected_claim_results"
        ]
    }


def _relationship_for_claim(
    expected_claim_result: dict[str, Any],
) -> str | None:
    """Return benchmark-defined evidence relationship.

    Week 26 relationship reasoning must use explicit benchmark
    metadata rather than infer relationships from lexical similarity.
    """

    relationship = expected_claim_result.get(
        "expected_relationship_dependency"
    )

    if relationship == "NOT_APPLICABLE":
        return None

    return relationship


def _evidence_for_claim(
    case: dict[str, Any],
    claim: dict[str, Any],
    expected_claim_result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return evidence to be evaluated for the claim.

    For relationship adversarial cases, all explicitly cited evidence
    must remain visible to the relationship evaluator.

    This is essential because:

    - C001 tests unsafe composition across multiple sources;
    - C012 tests explicit disagreement between multiple sources.
    """

    evidence_by_id = {
        evidence[
            "evidence_id"
        ]: evidence
        for evidence
        in case[
            "evidence_items"
        ]
    }

    citation_to_evidence_id = {
        citation[
            "citation_id"
        ]: citation[
            "evidence_id"
        ]
        for citation
        in case[
            "citation_index"
        ]
    }

    evidence_ids: list[str] = []

    for citation_id in claim.get(
        "citation_ids",
        [],
    ):
        evidence_id = (
            citation_to_evidence_id.get(
                citation_id
            )
        )

        if (
            evidence_id is not None
            and evidence_id
            not in evidence_ids
        ):
            evidence_ids.append(
                evidence_id
            )

    for evidence_id in expected_claim_result.get(
        "required_evidence_ids",
        [],
    ):
        if evidence_id not in evidence_ids:
            evidence_ids.append(
                evidence_id
            )

    return [
        evidence_by_id[
            evidence_id
        ]
        for evidence_id
        in evidence_ids
        if evidence_id
        in evidence_by_id
    ]


def _run_claim(
    case: dict[str, Any],
    claim: dict[str, Any],
    expected_claim_result: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one claim through relationship-aware groundedness."""

    relationship = (
        _relationship_for_claim(
            expected_claim_result
        )
    )

    evidence_items = (
        _evidence_for_claim(
            case,
            claim,
            expected_claim_result,
        )
    )

    result = (
        assess_relationship_aware_groundedness(
            claim_id=claim[
                "claim_id"
            ],
            claim_text=claim[
                "text"
            ],
            evidence_items=evidence_items,
            relationship=relationship,
            material=claim.get(
                "material",
                True,
            ),
        )
    )

    expected_groundedness = (
        expected_claim_result[
            "expected_groundedness_status"
        ]
    )

    actual_groundedness = result[
        "groundedness_status"
    ]

    groundedness_matches = (
        expected_groundedness
        == actual_groundedness
    )

    failure_reasons = []

    if not groundedness_matches:
        failure_reasons.append(
            "Groundedness mismatch: "
            f"expected {expected_groundedness}, "
            f"got {actual_groundedness}"
        )

    return {
        "claim_id": claim[
            "claim_id"
        ],
        "claim_text": claim[
            "text"
        ],
        "relationship": relationship,
        "expected_groundedness_status": (
            expected_groundedness
        ),
        "actual_groundedness_status": (
            actual_groundedness
        ),
        "groundedness_matches": (
            groundedness_matches
        ),
        "relationship_result": result[
            "relationship_result"
        ],
        "composition_allowed": result[
            "composition_allowed"
        ],
        "lifecycle_valid": result[
            "lifecycle_valid"
        ],
        "source_level_results": result[
            "source_level_results"
        ],
        "supported_components": result[
            "supported_components"
        ],
        "unsupported_components": result[
            "unsupported_components"
        ],
        "contradictory_components": result[
            "contradictory_components"
        ],
        "final_reason": result[
            "final_reason"
        ],
        "failure_reasons": (
            failure_reasons
        ),
    }


def _run_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate one focused Week 26 relationship case."""

    expected_lookup = (
        _expected_claim_result_lookup(
            case
        )
    )

    claim_results = []

    for claim in case[
        "candidate_claims"
    ]:
        claim_id = claim[
            "claim_id"
        ]

        expected = (
            expected_lookup.get(
                claim_id
            )
        )

        if expected is None:
            raise ValueError(
                f"{case['case_id']} has no expected result "
                f"for {claim_id}."
            )

        claim_results.append(
            _run_claim(
                case,
                claim,
                expected,
            )
        )

    case_match = all(
        result[
            "groundedness_matches"
        ]
        for result
        in claim_results
    )

    failure_reasons = [
        failure
        for result
        in claim_results
        for failure
        in result[
            "failure_reasons"
        ]
    ]

    return {
        "case_id": case[
            "case_id"
        ],
        "case_name": case[
            "case_name"
        ],
        "threat_class": case[
            "threat_class"
        ],
        "expected_case_groundedness": case[
            "expected_groundedness_decision"
        ],
        "claim_results": (
            claim_results
        ),
        "case_match": (
            case_match
        ),
        "failure_reasons": (
            failure_reasons
        ),
    }


def _summarise(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarise focused relationship benchmark."""

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

    relationship_unverified_cases = []

    conflict_blocked_cases = []

    composition_allowed_cases = []

    for result in results:
        for claim_result in result[
            "claim_results"
        ]:
            status = claim_result[
                "actual_groundedness_status"
            ]

            if (
                status
                == "RELATIONSHIP_UNVERIFIED"
            ):
                relationship_unverified_cases.append(
                    result[
                        "case_id"
                    ]
                )

            if status == "CONFLICT_BLOCKED":
                conflict_blocked_cases.append(
                    result[
                        "case_id"
                    ]
                )

            if claim_result[
                "composition_allowed"
            ]:
                composition_allowed_cases.append(
                    result[
                        "case_id"
                    ]
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
        "relationship_unverified_case_ids": sorted(
            set(
                relationship_unverified_cases
            )
        ),
        "conflict_blocked_case_ids": sorted(
            set(
                conflict_blocked_cases
            )
        ),
        "composition_allowed_case_ids": sorted(
            set(
                composition_allowed_cases
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


def run_relationship_benchmark() -> dict[str, Any]:
    """Execute the focused Week 26 relationship benchmark."""

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

    output = {
        "benchmark_name": (
            "Week 26 Relationship-Aware "
            "Groundedness Benchmark"
        ),
        "benchmark_version": "1.0",
        "source_benchmark": benchmark[
            "benchmark_name"
        ],
        "evaluation_type": (
            "week26_relationship_aware_groundedness"
        ),
        "target_case_ids": list(
            TARGET_CASE_IDS
        ),
        "summary": (
            summary
        ),
        "results": (
            results
        ),
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
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output


def _print_summary(
    report: dict[str, Any],
) -> None:
    """Print concise benchmark result."""

    summary = report[
        "summary"
    ]

    print(
        "Week 26 Relationship-Aware Groundedness Benchmark"
    )

    print(
        "-------------------------------------------------"
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
        "Relationship-unverified cases: "
        f"{summary['relationship_unverified_case_ids']}"
    )

    print(
        "Conflict-blocked cases: "
        f"{summary['conflict_blocked_case_ids']}"
    )

    print(
        "Composition-allowed adversarial cases: "
        f"{summary['composition_allowed_case_ids']}"
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
        run_relationship_benchmark()
    )

    _print_summary(
        report
    )


if __name__ == "__main__":
    main()